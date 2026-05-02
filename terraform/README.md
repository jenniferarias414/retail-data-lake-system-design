# Terraform Proof of Concept

## Purpose

This Terraform configuration deploys a lightweight AWS proof-of-concept for the Retail Data Lake System Design project.

The full production architecture would include additional services such as Kinesis, Glue, Athena, QuickSight, Redshift, or Snowflake. This proof-of-concept intentionally deploys only a small, low-cost serverless slice of the larger design.

## Deployed Resources

Terraform creates:

- Raw S3 bucket for incoming retail event JSON files
- Curated S3 bucket for valid and invalid processed outputs
- Lambda function for validation and PII masking
- IAM role and policy for Lambda permissions
- S3 event notification to trigger Lambda when JSON files land in the raw bucket

## Proof-of-Concept Flow

```text
Upload JSON event to raw S3 bucket
    → S3 object-created event triggers Lambda
    → Lambda validates required fields
    → Lambda masks email and phone fields
    → Valid record is written to silver/retail_events/
    → Invalid record is written to errors/retail_events/
    → Processing activity is logged in CloudWatch
```

## Deploy

From the `terraform` folder:

```bash
terraform init
terraform plan
terraform apply
```

## Upload Sample Files

After deployment, Terraform outputs sample AWS CLI commands.

Example:

```bash
aws s3 cp ../sample_data/pos_event_valid.json s3://<raw-bucket-name>/incoming/pos_event_valid.json
```

## Verify Outputs

Valid records are written to:

```text
s3://<curated-bucket-name>/silver/retail_events/
```

Invalid records are written to:

```text
s3://<curated-bucket-name>/errors/retail_events/
```

## Cleanup

Destroy all resources after testing:

```bash
terraform destroy
```

## Cost Control

This proof-of-concept avoids deploying higher-cost services such as Glue jobs, Redshift clusters, QuickSight dashboards, or Kinesis streams.

The expected cost for a brief low-volume demo should be very small, but AWS costs depend on account usage, region, and resource activity. Always destroy resources when finished.