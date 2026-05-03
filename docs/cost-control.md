# Cost Control Plan

## Purpose

This document explains the cost-control strategy for the Retail Data Lake System Design project.

The full future-state architecture includes services such as Kinesis, Glue, Athena, QuickSight, Redshift, Snowflake, and SageMaker. Those services can be appropriate for production, but they may create unnecessary cost for a small proof-of-concept.

This project intentionally deploys only a small AWS slice to demonstrate the raw-to-curated validation pattern.

---

## Cost-Control Strategy

The proof-of-concept is designed to keep cloud usage minimal.

It deploys only:

- Two Amazon S3 buckets
- One AWS Lambda function
- One IAM role and policy
- One S3 event notification
- CloudWatch logging from Lambda execution

It does not deploy:

- AWS Glue jobs
- Redshift clusters
- QuickSight dashboards
- Kinesis streams
- SageMaker notebooks or endpoints
- Long-running compute
- Databases
- Warehouses

---

## Why the Proof-of-Concept Is Small

The assignment requires a future-state architecture design for a retail data lake.

The full architecture would support:

- Real-time ingestion
- Batch ingestion
- Data lake storage
- Transformation
- Governance
- BI reporting
- Machine learning

However, deploying all of those services just to prove the concept would add unnecessary cost, setup time, and operational complexity.

Instead, this project deploys one focused slice:

```text
S3 raw upload
    → Lambda validation
    → S3 curated/error output
    → CloudWatch logs
```

This slice proves the core pattern of moving raw data toward a curated layer while applying validation, PII masking, and error routing.

---

## Services With Potential Production Cost

The following services are part of the future-state design but are not deployed in the lightweight proof-of-concept.

| Service | Cost Consideration |
|---|---|
| AWS Glue | Charged based on job runtime and data processing resources |
| Amazon Athena | Charged based on data scanned by queries |
| Amazon QuickSight | BI service with user/session/pricing model considerations |
| Amazon Redshift | Warehouse compute can incur ongoing cluster or serverless usage cost |
| Kinesis Firehose | Charged based on data ingested and delivered |
| SageMaker | Notebooks, training jobs, and endpoints may incur cost |
| Snowflake | Warehouse compute, storage, and cloud services usage are billed separately |

---

## Proof-of-Concept Cost Considerations

The proof-of-concept uses low-volume test files and short-lived resources.

Expected cost drivers are minimal:

| Resource | Cost Driver |
|---|---|
| S3 raw bucket | Storage for uploaded JSON sample files |
| S3 curated bucket | Storage for processed output JSON files |
| Lambda | Request count and execution duration |
| CloudWatch Logs | Small amount of log ingestion and storage |
| IAM | No direct cost for IAM role/policy itself |

Because the test data is tiny and Lambda execution is short-lived, the expected cost should be very small for a brief demo.

Actual costs depend on account usage, region, retained logs, storage duration, and AWS pricing.

---

## Cleanup Process

After testing and screenshots, resources should be destroyed with Terraform:

```bash
cd terraform
export AWS_PROFILE=retail-poc
terraform destroy -var="aws_region=us-east-2"
```

Because S3 buckets cannot be deleted while objects remain inside them, sample files may need to be removed first:

```bash
aws s3 rm s3://<raw-bucket-name> --recursive
aws s3 rm s3://<curated-bucket-name> --recursive
```

Then rerun:

```bash
terraform destroy -var="aws_region=us-east-2"
```

---

## Local Files Not Committed

The repository `.gitignore` excludes local Terraform and output files that should not be committed.

Ignored examples:

```text
terraform/.terraform/
terraform/terraform.tfstate
terraform/terraform.tfstate.*
terraform/*.zip
outputs/
.env
*.pem
*.key
```

This prevents local state, generated packages, credentials, and temporary output files from being pushed to GitHub.

---

## Production Cost Recommendations

A production implementation should include stronger cost-control practices.

Recommended practices:

- Use AWS Budgets and billing alerts
- Apply S3 lifecycle policies for archival and retention
- Store analytics data in compressed columnar formats such as Parquet
- Partition data by query patterns such as date, region, or source
- Avoid querying raw JSON when curated Parquet is available
- Use Athena workgroups with query limits
- Right-size Glue jobs and monitor job runtime
- Avoid always-on compute when serverless or scheduled compute is enough
- Use Redshift or Snowflake warehouse auto-suspend where applicable
- Monitor dashboard refresh frequency
- Delete or archive obsolete datasets
- Tag resources by project, environment, owner, and cost center

---

## Cost-Aware Architecture Choices

| Design Choice | Cost Benefit |
|---|---|
| S3 as central storage | Low-cost durable storage for many data types |
| Lambda for small validation proof-of-concept | Pay-per-use and no idle compute |
| Avoiding Redshift deployment in the demo | Prevents ongoing warehouse cost |
| Avoiding Glue jobs in the demo | Prevents job runtime charges |
| Terraform destroy workflow | Makes cleanup repeatable |
| Small sample files | Keeps storage and processing cost minimal |
| Screenshots instead of persistent infrastructure | Preserves proof without leaving services running |

---

## Key Takeaway

Cost control is part of good system design.

The production architecture is intentionally scalable, but the proof-of-concept is intentionally small. This allows the project to demonstrate a realistic AWS data lake pattern without deploying unnecessary services or creating avoidable cloud costs.