## Retail Data Lake System Design on AWS

## Overview

This project designs a future-state cloud data lake architecture for a global retail company.

XYZ Retail operates across physical stores, mobile apps, web commerce, and internal business systems. The company needs a centralized data platform that can support near real-time insights, governed access, self-service reporting, and advanced analytics.

This project includes:

- A future-state AWS data lake architecture
- Source-to-target data flow mapping
- Business requirement to technology mapping
- Security, governance, and cost-control considerations
- A lightweight AWS proof-of-concept that validates raw retail event files and writes curated outputs to Amazon S3

The proof-of-concept demonstrates one small slice of the larger architecture:

```text
Raw retail event file → S3 raw zone → Lambda validation → S3 curated/error zone → CloudWatch logs
```

---

## Why This Matters

Retail companies generate data across many systems:

- Point-of-sale transactions from physical stores
- Web and mobile app behavior
- E-commerce orders
- Inventory and supply chain data
- Customer and marketing data

When this data is siloed, business teams may see delayed reports, inconsistent metrics, duplicated storage, and limited ability to respond quickly.

A centralized data lake helps teams combine these sources into one governed platform for analytics, machine learning, and business reporting.

---

## Business Problem

XYZ Retail currently faces:

- Overnight batch reporting and delayed analytics
- Inconsistent metrics across sales, marketing, and inventory teams
- High maintenance costs from on-premise systems and multiple ETL tools
- Limited scalability for new regions, mobile apps, and IoT data
- Compliance gaps around personally identifiable information (PII)

The goal is to reduce reporting latency from 24 hours to approximately 1 hour while improving data quality, governance, and self-service analytics.

---

## Key Business Terms

### POS — Point of Sale

A point-of-sale system captures in-store transactions such as purchases, refunds, store location, cashier activity, and payment events.

### ERP — Enterprise Resource Planning

An ERP system tracks core business operations such as inventory, finance, procurement, and supply chain activity.

### CRM — Customer Relationship Management

A CRM system stores customer profiles, marketing engagement, loyalty activity, and sales/customer service interactions.

### PII — Personally Identifiable Information

PII includes sensitive customer information such as email, phone number, address, and customer name. This data requires encryption, masking, role-based access control, and audit logging.

---

## What This Project Covers

- AWS data lake architecture
- Batch and near real-time ingestion patterns
- S3 raw and curated zones
- Serverless event validation with AWS Lambda
- Data quality checks
- PII detection and masking strategy
- Bronze, Silver, and Gold data layers
- Athena/QuickSight analytics serving pattern
- Snowflake vs Redshift platform decision
- Cost-control and operational considerations

---

## Architecture Overview

The proposed architecture uses Amazon S3 as the centralized data lake foundation.

Near real-time event sources such as POS, mobile app, and e-commerce orders can flow through API Gateway, Kinesis Firehose, or Lambda into the raw data zone.

Batch sources such as ERP and CRM datasets can be ingested on a schedule using AWS Glue.

Data moves through progressive quality layers:

```text
Bronze / Raw → Silver / Cleaned → Gold / Analytics-Ready
```

The curated data can then be queried with Athena, visualized in QuickSight, loaded into Redshift or Snowflake, or used by SageMaker for machine learning workflows.

---

## Future-State Data Flow

### Near Real-Time Sources

```text
POS / Mobile App / E-commerce Events
    → API Gateway or Kinesis Firehose
    → S3 Bronze Zone
    → Lambda/Glue validation
    → S3 Silver Zone
```

### Batch Sources

```text
ERP / CRM datasets
    → Scheduled Glue ingestion
    → S3 Bronze Zone
    → Glue transformation
    → S3 Silver/Gold Zones
```

### Analytics Consumption

```text
Gold datasets
    → Athena / QuickSight / SageMaker / Redshift / Snowflake
```

---

## Lightweight AWS Proof of Concept

The full production architecture would require multiple AWS services and larger datasets.

To keep this project cost-conscious, the proof-of-concept implements a small serverless slice:

```text
S3 Raw Bucket → Lambda Validator → S3 Curated Bucket → CloudWatch Logs
```

When a sample retail event JSON file is uploaded to the raw S3 bucket, Lambda validates the event, adds processing metadata, masks sensitive fields where applicable, and writes the result to the curated zone.

Invalid records are routed to an error prefix for review.

---

## Proof-of-Concept Flow

1. Upload a sample POS or e-commerce JSON event to the raw S3 bucket
2. S3 event notification triggers the Lambda function
3. Lambda reads the raw JSON file
4. Required fields are validated
5. PII fields are masked
6. Valid records are written to the curated S3 zone
7. Invalid records are written to the error zone
8. Processing activity is visible in CloudWatch logs

---

## Example Raw Event

```json
{
  "event_id": "evt_pos_1001",
  "event_type": "pos_transaction",
  "customer_id": "cust_501",
  "store_id": "store_22",
  "transaction_total": 84.52,
  "email": "customer@example.com",
  "phone": "555-123-4567",
  "event_timestamp": "2026-05-02T10:15:00Z"
}
```

---

## Example Curated Event

```json
{
  "event_id": "evt_pos_1001",
  "event_type": "pos_transaction",
  "customer_id": "cust_501",
  "store_id": "store_22",
  "transaction_total": 84.52,
  "email": "c******r@example.com",
  "phone": "***-***-4567",
  "event_timestamp": "2026-05-02T10:15:00Z",
  "validation_status": "valid",
  "pipeline_layer": "silver",
  "processed_at": "2026-05-02T10:16:04Z"
}
```

---

## Requirements Mapping

| Requirement | Architecture Choice |
|---|---|
| Reduce report latency from 24 hours to 1 hour | Near real-time ingestion for POS, mobile app, and e-commerce events |
| Consolidate retail, CRM, and operational data | Centralized Amazon S3 data lake |
| Support self-service reporting | Glue Data Catalog, Athena, and QuickSight |
| Support predictive analytics | Curated Silver/Gold datasets available for SageMaker |
| Protect PII | IAM, encryption, masking, role-based access control, and audit logging |
| Support 3–5x growth | Serverless services, S3 scalability, and partitioned data design |
| Improve data quality | Validation rules, curated zone, and error routing |

---

## Platform Decision: Snowflake vs Redshift

This architecture can support either Snowflake or Redshift as the analytical warehouse layer.

### Snowflake is a strong fit when:

- The organization wants minimal infrastructure management
- Workloads are spiky or vary by team
- Secure data sharing is important
- Multiple teams need isolated compute resources
- Multi-cloud flexibility is a priority

### Redshift is a strong fit when:

- The organization is already AWS-native
- IAM, VPC, and AWS-native controls are preferred
- Workloads are predictable
- The data engineering team is comfortable tuning warehouse performance
- Redshift Spectrum is useful for querying data in S3

For this design, the primary foundation is Amazon S3 as the centralized data lake. Snowflake or Redshift can be added as the warehouse layer depending on business and platform constraints.

---

## Cost-Control Notes

This proof-of-concept intentionally avoids deploying expensive services such as Glue jobs, Redshift clusters, QuickSight dashboards, or Kinesis streams by default.

The demo focuses on low-volume S3 and Lambda usage to demonstrate the raw-to-curated validation pattern with minimal cloud cost.

Recommended cleanup after testing:

```bash
terraform destroy
```

---

## Planned Screenshots

Screenshots will be added after the proof-of-concept is deployed.

Planned screenshots:

- Architecture diagram
- Terraform apply
- Raw S3 upload
- Lambda CloudWatch logs
- Curated S3 output
- Error record routing
- GitHub README

---

## How to Deploy the Proof of Concept

Navigate to the Terraform folder:

```bash
cd terraform
```

Initialize Terraform:

```bash
terraform init
```

Preview resources:

```bash
terraform plan
```

Deploy:

```bash
terraform apply
```

Upload a sample event to the raw S3 bucket:

```bash
aws s3 cp ../sample_data/pos_event_valid.json s3://<raw-bucket-name>/incoming/
```

Check the curated output bucket:

```bash
aws s3 ls s3://<curated-bucket-name>/silver/
```

Destroy resources after testing:

```bash
terraform destroy
```

---

## Key Takeaway

This project demonstrates how a retail company can modernize siloed data systems into a centralized, governed data lake.

The full design supports near real-time ingestion, batch processing, medallion architecture, self-service BI, and machine learning readiness.

The lightweight AWS proof-of-concept shows how raw retail events can be validated, masked, and routed into curated storage using serverless services.

---

## Real-World Data Engineering Connection

This project mirrors common data engineering work in large organizations:

- Designing source-to-target data flows
- Separating raw and curated data layers
- Applying data quality checks before analytics consumption
- Protecting sensitive customer data
- Building cloud-native, scalable data platforms
- Documenting architecture decisions and tradeoffs
- Creating lightweight proof-of-concepts before full production implementation

---

## References

- AWS Lambda with Amazon S3 event notifications
- Amazon S3 documentation
- AWS Glue Data Catalog documentation
- Amazon Athena documentation
- AWS Well-Architected Framework
