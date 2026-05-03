# Operational Runbook

## Purpose

This runbook explains how to deploy, test, verify, and clean up the Retail Data Lake proof-of-concept.

The proof-of-concept implements a small serverless validation slice of the larger retail data lake architecture.

```text
Raw S3 bucket
    → S3 object-created event
    → Lambda validator
    → Curated S3 bucket
    → CloudWatch logs
```

---

## Prerequisites

Before running the proof-of-concept, confirm the following tools are installed and configured:

- Terraform
- AWS CLI
- Python 3
- Git

A personal AWS CLI profile should be configured before deployment.

Example profile name:

```text
retail-poc
```

---

## AWS Profile Setup

This project uses a named AWS CLI profile to avoid mixing personal demo resources with work or default AWS credentials.

Configure a named profile:

```bash
aws configure --profile retail-poc
```

Enter:

```text
AWS Access Key ID: <personal access key>
AWS Secret Access Key: <personal secret key>
Default region name: us-east-2
Default output format: json
```

Verify the profile:

```bash
aws sts get-caller-identity --profile retail-poc
```

The returned account should be the intended personal AWS account.

---

## Terraform Initialization

Navigate to the Terraform folder:

```bash
cd terraform
```

Set the AWS profile for the current terminal session:

```bash
export AWS_PROFILE=retail-poc
```

Initialize Terraform:

```bash
terraform init
```

Validate the configuration:

```bash
terraform validate
```

Format the Terraform files:

```bash
terraform fmt
```

---

## Preview the Deployment

Run a Terraform plan:

```bash
terraform plan -var="aws_region=us-east-2"
```

The plan should show AWS resources to create, including:

- Raw S3 bucket
- Curated S3 bucket
- Lambda function
- IAM role and policy
- S3 event notification
- S3 public access blocks
- S3 encryption configuration

Expected summary:

```text
Plan: 12 to add, 0 to change, 0 to destroy.
```

---

## Deploy the Proof-of-Concept

Apply the Terraform configuration:

```bash
terraform apply -var="aws_region=us-east-2"
```

When prompted, type:

```text
yes
```

After deployment, Terraform outputs include:

- Raw bucket name
- Curated bucket name
- Lambda function name
- Sample upload commands
- S3 list commands for curated and error outputs

---

## Upload Sample Events

From the `terraform` folder, upload the valid POS event:

```bash
aws s3 cp ../sample_data/pos_event_valid.json s3://<raw-bucket-name>/incoming/pos_event_valid.json
```

Upload the valid e-commerce event:

```bash
aws s3 cp ../sample_data/ecommerce_event_valid.json s3://<raw-bucket-name>/incoming/ecommerce_event_valid.json
```

Upload the invalid POS event:

```bash
aws s3 cp ../sample_data/pos_event_invalid_missing_customer_id.json s3://<raw-bucket-name>/incoming/pos_event_invalid_missing_customer_id.json
```

The S3 event notification triggers Lambda automatically for JSON files uploaded under the `incoming/` prefix.

---

## Verify Valid Outputs

List valid curated outputs:

```bash
aws s3 ls s3://<curated-bucket-name>/silver/retail_events/
```

Expected valid files:

```text
ecommerce_event_valid.json
pos_event_valid.json
```

Download and inspect a valid output:

```bash
mkdir -p ../outputs
aws s3 cp s3://<curated-bucket-name>/silver/retail_events/pos_event_valid.json ../outputs/pos_event_curated.json
cat ../outputs/pos_event_curated.json
```

Expected result:

- Email is masked
- Phone is masked
- `_metadata.validation_status` is `valid`
- `_metadata.pipeline_layer` is `silver`

---

## Verify Invalid Output

List invalid/error outputs:

```bash
aws s3 ls s3://<curated-bucket-name>/errors/retail_events/
```

Expected invalid file:

```text
pos_event_invalid_missing_customer_id.json
```

Download and inspect the invalid output:

```bash
aws s3 cp s3://<curated-bucket-name>/errors/retail_events/pos_event_invalid_missing_customer_id.json ../outputs/pos_event_error.json
cat ../outputs/pos_event_error.json
```

Expected result:

- `_metadata.validation_status` is `invalid`
- `_metadata.pipeline_layer` is `error`
- `_metadata.validation_errors` includes `Missing required field: customer_id`

---

## Verify in AWS Console

Set the AWS Console region to:

```text
US East (Ohio) / us-east-2
```

Recommended screenshot locations:

| Screenshot | AWS Console Location |
|---|---|
| Raw S3 upload | S3 → raw bucket → `incoming/` |
| Lambda trigger | Lambda → validator function → S3 trigger |
| Curated output | S3 → curated bucket → `silver/retail_events/` |
| Error output | S3 → curated bucket → `errors/retail_events/` |
| CloudWatch logs | Lambda → Monitor → View CloudWatch logs |

---

## CloudWatch Verification

In CloudWatch logs, look for records showing:

- Source bucket
- Source key
- Target bucket
- Output key
- Validation status
- Validation errors, if any

Example successful status:

```text
"validation_status": "valid"
```

Example invalid status:

```text
"validation_status": "invalid"
```

---

## Cleanup

After screenshots and validation are complete, destroy the resources.

From the `terraform` folder:

```bash
export AWS_PROFILE=retail-poc
terraform destroy -var="aws_region=us-east-2"
```

When prompted, type:

```text
yes
```

If Terraform cannot delete the S3 buckets because they contain files, empty the buckets:

```bash
aws s3 rm s3://<raw-bucket-name> --recursive
aws s3 rm s3://<curated-bucket-name> --recursive
```

Then rerun:

```bash
terraform destroy -var="aws_region=us-east-2"
```

Expected result:

```text
Destroy complete!
```

---

## Common Issues

### Terraform says AWS credentials are missing

Confirm the profile exists:

```bash
aws configure list-profiles
```

Set the profile:

```bash
export AWS_PROFILE=retail-poc
```

Verify identity:

```bash
aws sts get-caller-identity --profile retail-poc
```

---

### Terraform says a variable is undeclared

This usually means Terraform was run from the wrong folder.

Run Terraform commands from:

```text
terraform/
```

Not the project root.

---

### S3 bucket cannot be destroyed

S3 buckets must be empty before deletion.

Empty buckets with:

```bash
aws s3 rm s3://<bucket-name> --recursive
```

Then rerun Terraform destroy.

---

### Lambda does not trigger

Check:

- File was uploaded under `incoming/`
- File suffix is `.json`
- S3 notification exists on the raw bucket
- Lambda permission allows S3 invocation
- AWS Console region is `us-east-2`

---

## Key Takeaway

This proof-of-concept is intentionally small but operationally complete.

It demonstrates the workflow of deploying infrastructure with Terraform, uploading raw retail events to S3, triggering Lambda validation, routing valid and invalid records, inspecting CloudWatch logs, and destroying resources after validation.