# Screenshots

This folder contains screenshots from the Retail Data Lake System Design proof-of-concept.

The screenshots document the deployment and validation flow:

```text
Terraform deploys AWS resources
    → sample retail events are uploaded to the raw S3 bucket
    → S3 triggers Lambda
    → Lambda validates and masks records
    → valid records are written to the curated Silver zone
    → invalid records are routed to the error zone
    → CloudWatch logs capture processing activity
```

## Screenshot List

| File | Description |
|---|---|
| `01_terraform_plan.png` | Terraform plan showing AWS resources to be created |
| `02_terraform_apply_outputs.png` | Terraform apply outputs with bucket names, Lambda name, and sample CLI commands |
| `03_raw_s3_upload.png` | Raw S3 bucket showing uploaded sample JSON files |
| `04_lambda_s3_trigger.png` | Lambda function configured with an S3 object-created trigger |
| `05_curated_s3_output.png` | Curated S3 Silver zone showing valid processed records |
| `06_error_record_output.png` | Error zone showing invalid record routing |
| `07_cloudwatch_logs.png` | CloudWatch logs showing Lambda processing and validation output |
| `08_terminal_valid_curated_output.png` | Terminal output showing a valid curated record with masked PII and metadata |
| `09_terminal_invalid_error_output.png` | Terminal output showing an invalid record with validation error metadata |

## Notes

These screenshots are from a short-lived personal AWS proof-of-concept. Resources were deployed with Terraform and should be destroyed after validation to avoid unnecessary cost.