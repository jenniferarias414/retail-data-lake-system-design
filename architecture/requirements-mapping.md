# Requirements Mapping

## Purpose

This document maps XYZ Retail's business and technical requirements to the proposed architecture choices.

The goal is to show why each major technology or design pattern was selected, what business value it provides, and what risks should be considered.

---

## Summary Table

| Requirement | Architecture Choice | Why This Choice Fits | Risks / Mitigations |
|---|---|---|---|
| Reduce report latency from 24 hours to approximately 1 hour | Near real-time ingestion for POS, mobile app, and e-commerce events using API Gateway, Kinesis Firehose, or Lambda | Event-driven ingestion makes high-value sales and customer behavior data available faster than overnight batch ETL | Streaming adds operational complexity; mitigate with monitoring, retries, and clear failure handling |
| Consolidate retail, CRM, and operational data | Centralized Amazon S3 data lake | S3 provides scalable, durable, cost-effective storage for structured and semi-structured data from many systems | A data lake can become disorganized; mitigate with Bronze/Silver/Gold zones, naming standards, and metadata cataloging |
| Support both real-time and batch sources | Separate ingestion patterns for streaming/event data and scheduled ERP/CRM loads | POS/app/e-commerce events benefit from faster ingestion, while ERP/CRM data can be processed in scheduled batches | Multiple ingestion paths increase complexity; mitigate with documentation, orchestration, and standardized logging |
| Support self-service reporting | Glue Data Catalog, Athena, and QuickSight | Analysts can query curated data in S3 and build dashboards without waiting on custom extracts | Athena query costs can grow if data is not optimized; mitigate with Parquet, partitioning, and curated Gold datasets |
| Enable predictive analytics and customer segmentation | Curated Silver and Gold datasets available to SageMaker or other ML tools | Data scientists need cleaned, consistent, historical datasets for model training and analysis | Poor data quality impacts models; mitigate with validation rules, freshness checks, and curated feature-ready datasets |
| Protect personally identifiable information | IAM, encryption, PII masking, role-based access control, and audit logging | Retail data includes emails, phone numbers, addresses, and customer identifiers that require controlled access | Sensitive data exposure risk; mitigate with least privilege, masking/tokenization, encryption, and audit trails |
| Support 3-5x growth over 1-3 years | Serverless and scalable services such as S3, Glue, Lambda, Kinesis Firehose, Athena, and optional Snowflake/Redshift | Managed cloud services can scale storage and compute as data volume grows | Cost can grow with usage; mitigate with lifecycle policies, partitioning, query optimization, and budget alerts |
| Improve metric consistency across departments | Gold analytics layer with governed business definitions | Shared curated datasets reduce conflicting definitions across sales, marketing, inventory, and finance | Business logic can drift; mitigate with version-controlled transformations, documentation, and data ownership |
| Support inventory optimization | Combine POS, e-commerce, and ERP inventory data into curated Silver/Gold models | Inventory teams need both transaction activity and operational stock data to improve replenishment decisions | Late or missing source data can affect alerts; mitigate with freshness monitoring and error handling |
| Support abandoned-cart recovery | Near real-time web/mobile/e-commerce event ingestion | Marketing teams need timely online behavior data to act quickly on abandoned carts | Requires reliable event capture and customer identity matching; mitigate with schema contracts and customer ID standardization |
| Improve operational monitoring | CloudWatch logs, error prefixes, and pipeline status visibility | Engineering teams need to detect failures, troubleshoot bad records, and verify data movement | Logs alone may not be enough in production; expand with dashboards, alarms, and data quality monitoring |
| Reduce on-prem maintenance burden | Cloud-native managed services | Managed services reduce infrastructure operations compared with on-prem systems and custom ETL servers | Vendor cost and service dependency; mitigate with cost monitoring and portable data formats where possible |

---

## Source-to-Target Mapping

| Source System | Data Type | Ingestion Pattern | Raw Landing Zone | Curated Output | Primary Consumers |
|---|---|---|---|---|---|
| Point-of-Sale system | In-store transaction events | Near real-time event ingestion | S3 Bronze POS prefix | Silver retail events, Gold sales facts | Store managers, inventory managers, analysts |
| Mobile application | Clickstream and app interaction events | Near real-time API or streaming ingestion | S3 Bronze app prefix | Silver customer behavior events, Gold engagement metrics | Product owners, marketing analysts, data scientists |
| Web application | Page views, clicks, cart events | Near real-time API or streaming ingestion | S3 Bronze web prefix | Silver web events, Gold funnel metrics | Product owners, marketing analysts |
| E-commerce platform | Orders, carts, customer activity | Near real-time or micro-batch ingestion | S3 Bronze e-commerce prefix | Silver orders, Gold online sales metrics | E-commerce team, marketing analysts, executives |
| ERP system | Inventory, finance, procurement, supply chain | Scheduled batch ingestion | S3 Bronze ERP prefix | Silver operational datasets, Gold inventory KPIs | Inventory managers, finance, operations |
| CRM system | Customer profiles, leads, campaigns, engagement | Scheduled batch ingestion | S3 Bronze CRM prefix | Silver customer profiles, Gold customer segments | Marketing analysts, customer analytics, data scientists |

---

## Architecture Layer Mapping

| Layer | Purpose | Example AWS Services | Business Value |
|---|---|---|---|
| Source Layer | Systems that generate retail, customer, and operational data | POS systems, mobile apps, e-commerce platform, ERP, CRM | Captures the full view of customer and business activity |
| Ingestion Layer | Moves source data into the cloud platform | API Gateway, Kinesis Firehose, Lambda, Glue | Supports both near real-time and batch data movement |
| Bronze Layer | Stores raw source-aligned data | Amazon S3 | Enables replay, audit, backfill, and traceability |
| Silver Layer | Cleans, validates, masks, and standardizes data | Lambda, Glue, S3 curated prefixes | Produces trusted reusable datasets |
| Gold Layer | Creates business-ready analytics models | Glue, dbt, Athena, Redshift, Snowflake | Enables reporting, KPIs, segmentation, and dashboards |
| Governance Layer | Controls access, metadata, and auditability | IAM, KMS, Glue Data Catalog, CloudWatch | Protects sensitive data and improves trust |
| Consumption Layer | Serves data to end users and downstream systems | Athena, QuickSight, SageMaker, Redshift, Snowflake | Enables self-service BI, ML, and business decision-making |

---

## Technology Choice Details

### Amazon S3

Amazon S3 is selected as the centralized data lake foundation because it is scalable, durable, cost-effective, and integrates with AWS analytics and machine learning services.

It supports many data formats and can store raw, cleaned, curated, and archived datasets.

### AWS Lambda

AWS Lambda is selected for the proof-of-concept because it is well suited for lightweight, event-driven validation when files land in S3.

It is not intended to perform large-scale transformations in this design. Large transformations would be handled by Glue, Spark, dbt, Redshift, or Snowflake.

### AWS Glue

AWS Glue is recommended for production-scale batch ingestion and transformation because it supports serverless Spark, crawlers, the Glue Data Catalog, and integration with S3-based data lakes.

### Kinesis Firehose

Kinesis Firehose is recommended for near real-time delivery of POS, mobile, web, and e-commerce events into the data lake.

It is useful when the goal is to reliably deliver event data into S3 or an analytical destination with minimal operational overhead.

### Glue Data Catalog

The Glue Data Catalog is recommended as the metadata layer so that datasets in S3 can be discovered, cataloged, and queried by services such as Athena.

### Athena

Athena is recommended for serverless SQL querying over curated S3 datasets.

It is useful for cost-conscious analytics when data is stored in efficient formats and partitioned appropriately.

### QuickSight

QuickSight is recommended as a BI tool for dashboards and reporting.

It can support self-service analytics for business analysts, inventory managers, and executives.

### SageMaker

SageMaker is recommended for advanced analytics and machine learning workloads such as customer segmentation, demand forecasting, and recommendation use cases.

### Redshift or Snowflake

Redshift or Snowflake can be added as the warehouse layer depending on platform requirements.

Redshift is a strong fit for AWS-native teams with predictable workloads and existing AWS security patterns.

Snowflake is a strong fit for multi-team environments, spiky workloads, data sharing, and minimal infrastructure management.

---

## Benefits

The proposed architecture provides these benefits:

- Lower report latency
- Centralized data storage
- Better data quality
- Improved metric consistency
- Secure handling of customer data
- Scalable storage and processing
- Support for both batch and near real-time use cases
- Self-service analytics
- ML-ready curated datasets
- Reduced dependency on on-prem systems and fragmented ETL tools

---

## Key Risks and Mitigations

| Risk | Description | Mitigation |
|---|---|---|
| Data lake sprawl | Raw data can become difficult to manage without structure | Use clear Bronze/Silver/Gold zones, naming standards, and cataloging |
| PII exposure | Customer data may include emails, phones, addresses, and identifiers | Apply masking, encryption, IAM, role-based access, and audit logging |
| Streaming complexity | Near real-time pipelines introduce retries, ordering, and monitoring needs | Start with critical event streams only; add monitoring, DLQs, and replay strategy |
| Cost growth | Athena scans, Glue jobs, streaming services, and warehouse usage can increase cost | Use budgets, lifecycle policies, partitioning, efficient formats, and cleanup processes |
| Inconsistent business definitions | Different teams may define metrics differently | Use Gold-layer curated datasets with documented business logic |
| Bad source data | Missing fields, invalid types, duplicate events, or schema changes can break pipelines | Add validation rules, schema checks, and error routing |
| Overbuilding too early | Deploying every service at once can increase cost and complexity | Start with a proof-of-concept slice and expand incrementally |

---

## Proof-of-Concept Requirement Coverage

The lightweight AWS proof-of-concept covers a focused subset of the full design.

| Proof-of-Concept Feature | Requirement Demonstrated |
|---|---|
| Raw S3 bucket | Bronze/raw landing zone |
| S3 object-created trigger | Event-driven ingestion pattern |
| Lambda validator | Lightweight validation and transformation |
| PII masking | Sensitive data protection |
| Curated S3 output | Silver/cleaned data zone |
| Error output prefix | Bad record handling |
| CloudWatch logs | Operational visibility |
| Terraform deployment | Repeatable infrastructure-as-code |

---

## Key Takeaway

This architecture maps business needs to practical cloud data engineering patterns.

The design intentionally separates ingestion, storage, validation, transformation, governance, and consumption so each layer can scale independently and be maintained more easily.

The proof-of-concept validates one small but important production pattern: raw event ingestion, validation, sensitive-field masking, error routing, and curated output storage.