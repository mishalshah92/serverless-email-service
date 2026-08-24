output "api_endpoint" {
  description = "HTTP API endpoint."
  value       = aws_apigatewayv2_api.main.api_endpoint
}

output "table_name" {
  description = "DynamoDB table name."
  value       = aws_dynamodb_table.main.name
}

output "queue_url" {
  description = "SQS queue URL."
  value       = aws_sqs_queue.main.url
}

output "dlq_url" {
  description = "SQS DLQ URL."
  value       = aws_sqs_queue.dlq.url
}
