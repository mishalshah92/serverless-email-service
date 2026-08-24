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

resource "aws_lambda_permission" "api" {
  statement_id  = "AllowApiGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.intake.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.main.execution_arn}/*/*"
}
