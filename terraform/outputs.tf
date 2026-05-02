output "raw_bucket_name" {
  description = "S3 bucket where raw retail event JSON files should be uploaded."
  value       = aws_s3_bucket.raw.bucket
}

output "curated_bucket_name" {
  description = "S3 bucket where validated curated/error outputs are written."
  value       = aws_s3_bucket.curated.bucket
}

output "lambda_function_name" {
  description = "Name of the retail event validator Lambda function."
  value       = aws_lambda_function.validator.function_name
}

output "sample_upload_command_pos_event" {
  description = "AWS CLI command to upload the valid POS event sample."
  value       = "aws s3 cp ../sample_data/pos_event_valid.json s3://${aws_s3_bucket.raw.bucket}/incoming/pos_event_valid.json"
}

output "sample_upload_command_ecommerce_event" {
  description = "AWS CLI command to upload the valid e-commerce event sample."
  value       = "aws s3 cp ../sample_data/ecommerce_event_valid.json s3://${aws_s3_bucket.raw.bucket}/incoming/ecommerce_event_valid.json"
}

output "sample_upload_command_invalid_event" {
  description = "AWS CLI command to upload the invalid POS event sample."
  value       = "aws s3 cp ../sample_data/pos_event_invalid_missing_customer_id.json s3://${aws_s3_bucket.raw.bucket}/incoming/pos_event_invalid_missing_customer_id.json"
}

output "list_curated_outputs_command" {
  description = "AWS CLI command to list curated valid outputs."
  value       = "aws s3 ls s3://${aws_s3_bucket.curated.bucket}/silver/retail_events/"
}

output "list_error_outputs_command" {
  description = "AWS CLI command to list invalid/error outputs."
  value       = "aws s3 ls s3://${aws_s3_bucket.curated.bucket}/errors/retail_events/"
}