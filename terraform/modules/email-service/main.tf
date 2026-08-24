locals {
  name = "${var.project_name}-${var.website_name}-${var.deployment_name}"
}

resource "aws_dynamodb_table" "main" {
  name         = "${local.name}-config"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "pk"
  range_key    = "sk"

  attribute {
    name = "pk"
    type = "S"
  }

  attribute {
    name = "sk"
    type = "S"
  }

  server_side_encryption {
    enabled = true
  }

  tags = var.tags
}

resource "aws_sqs_queue" "dlq" {
  name                      = "${local.name}-email-dlq"
  message_retention_seconds = 1209600
  sqs_managed_sse_enabled   = true
  tags                      = var.tags
}

resource "aws_sqs_queue" "main" {
  name                       = "${local.name}-email"
  visibility_timeout_seconds = 90
  message_retention_seconds  = 345600
  sqs_managed_sse_enabled    = true

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 4
  })

  tags = var.tags
}

resource "aws_iam_role" "lambda" {
  name = "${local.name}-lambda"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "lambda.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })

  tags = var.tags
}

resource "aws_iam_role_policy" "lambda" {
  name = "${local.name}-lambda"
  role = aws_iam_role.lambda.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem"
        ]
        Resource = aws_dynamodb_table.main.arn
      },
      {
        Effect   = "Allow"
        Action   = ["sqs:SendMessage"]
        Resource = aws_sqs_queue.main.arn
      },
      {
        Effect   = "Allow"
        Action   = ["ses:SendEmail"]
        Resource = "*"
      },
      {
        Effect   = "Allow"
        Action   = ["ssm:GetParameter"]
        Resource = "*"
      }
    ]
  })
}

resource "aws_cloudwatch_log_group" "intake" {
  name              = "/aws/lambda/${local.name}-form-intake"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "worker" {
  name              = "/aws/lambda/${local.name}-email-worker"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_cloudwatch_log_group" "events" {
  name              = "/aws/lambda/${local.name}-email-events"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

resource "aws_lambda_function" "intake" {
  function_name = "${local.name}-form-intake"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.12"
  handler       = "email_service.api.handler.handle"
  filename      = var.lambda_package_path
  timeout       = 15
  memory_size   = 128

  environment {
    variables = {
      TABLE_NAME                      = aws_dynamodb_table.main.name
      QUEUE_URL                       = aws_sqs_queue.main.url
      TURNSTILE_SECRET_PARAMETER_NAME = var.turnstile_secret_parameter_name
    }
  }

  depends_on = [aws_cloudwatch_log_group.intake]
  tags       = var.tags
}

resource "aws_lambda_function" "worker" {
  function_name = "${local.name}-email-worker"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.12"
  handler       = "email_service.worker.handler.handle"
  filename      = var.lambda_package_path
  timeout       = 30
  memory_size   = 128

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
    }
  }

  depends_on = [aws_cloudwatch_log_group.worker]
  tags       = var.tags
}

resource "aws_lambda_function" "events" {
  function_name = "${local.name}-email-events"
  role          = aws_iam_role.lambda.arn
  runtime       = "python3.12"
  handler       = "email_service.events.handler.handle"
  filename      = var.lambda_package_path
  timeout       = 15
  memory_size   = 128

  environment {
    variables = {
      TABLE_NAME = aws_dynamodb_table.main.name
    }
  }

  depends_on = [aws_cloudwatch_log_group.events]
  tags       = var.tags
}

resource "aws_lambda_event_source_mapping" "worker" {
  event_source_arn        = aws_sqs_queue.main.arn
  function_name           = aws_lambda_function.worker.arn
  batch_size              = 10
  function_response_types = ["ReportBatchItemFailures"]
}

resource "aws_apigatewayv2_api" "main" {
  name          = "${local.name}-api"
  protocol_type = "HTTP"

  cors_configuration {
    allow_headers = ["content-type"]
    allow_methods = ["POST", "OPTIONS"]
    allow_origins = ["*"]
    max_age       = 300
  }

  tags = var.tags
}

resource "aws_apigatewayv2_integration" "intake" {
  api_id                 = aws_apigatewayv2_api.main.id
  integration_type       = "AWS_PROXY"
  integration_uri        = aws_lambda_function.intake.invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_route" "form_post" {
  api_id    = aws_apigatewayv2_api.main.id
  route_key = "POST /v1/forms/{form_id}"
  target    = "integrations/${aws_apigatewayv2_integration.intake.id}"
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.main.id
  name        = "$default"
  auto_deploy = true
  tags        = var.tags
}

resource "aws_lambda_permission" "api" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.intake.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}

resource "aws_cloudwatch_metric_alarm" "dlq_messages" {
  alarm_name          = "${local.name}-dlq-messages"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = 300
  statistic           = "Maximum"
  threshold           = 0
  treat_missing_data  = "notBreaching"

  dimensions = {
    QueueName = aws_sqs_queue.dlq.name
  }

  tags = var.tags
}
