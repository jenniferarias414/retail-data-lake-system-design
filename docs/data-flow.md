# Data Flow

## Purpose

This document explains how data moves through the Retail Data Lake System Design project.

It is intended as a reference aid for readers who are new to data lake architecture, medallion data layers, and source-to-target data flow design.

The page describes two related views:

- The full future-state architecture proposed for XYZ Retail
- The smaller proof-of-concept implemented in this repository

The proof-of-concept does not deploy every service in the future-state architecture. It implements one focused slice that demonstrates raw data landing, validation, PII masking, metadata enrichment, error routing, and curated output storage.

---

## High-Level Concept

XYZ Retail has data spread across physical stores, digital channels, and internal business systems.

The proposed data lake centralizes that data in Amazon S3, organizes it by quality level, and makes trusted datasets available for reporting, analytics, and machine learning.

At a high level, the future-state flow is:

```text
Source systems
    → Ingestion layer
    → S3 Bronze raw zone
    → Validation and transformation
    → S3 Silver cleansed zone
    → S3 Gold analytics zone
    → Analytics, BI, and machine learning consumers
```

This pattern separates the platform into clear responsibilities. Source systems produce data, ingestion services move data, storage layers preserve and organize data, processing services clean and transform data, and consumption tools serve business users.

---

## Source Systems

The future-state architecture supports multiple retail data sources.

| Source System | Example Data | Typical Freshness Need |
|---|---|---|
| Point-of-sale systems | In-store purchases, refunds, store location, payment method | Near real time |
| Mobile applications | App clicks, searches, cart activity, customer behavior | Near real time |
| Web applications | Page views, clicks, product views, checkout behavior | Near real time |
| E-commerce platform | Online orders, cart totals, checkout events, customer activity | Near real time or micro-batch |
| ERP system | Inventory, procurement, finance, supply chain, vendor data | Scheduled batch |
| CRM system | Customer profiles, loyalty activity, marketing campaigns, leads | Scheduled batch |

These sources do not all move through the platform in the same way. Event-style data benefits from faster ingestion, while operational datasets are often better handled through scheduled batch processing.

---

## Ingestion Patterns

The architecture uses different ingestion patterns based on how quickly the business needs the data and how the source system produces it.

### Near Real-Time Ingestion

Near real-time ingestion is recommended for high-value event data from POS, mobile, web, and e-commerce systems.

Examples include:

- A customer completes an in-store purchase
- A customer views a product in the mobile app
- A customer abandons a cart on the website
- An online order is submitted through the e-commerce platform

Proposed future-state flow:

```text
POS / mobile / web / e-commerce events
    → API Gateway, Lambda, Kinesis Data Streams, or Kinesis Firehose
    → S3 Bronze raw zone
    → Validation and enrichment
    → S3 Silver cleansed zone
    → Gold analytics datasets
```

This pattern helps reduce reporting latency and supports time-sensitive use cases such as inventory alerts, abandoned-cart recovery, store performance monitoring, and customer behavior analytics.

### Batch Ingestion

Batch ingestion is recommended for ERP and CRM datasets that are usually produced on a schedule.

Examples include:

- Daily inventory extracts from ERP
- Finance and procurement data from ERP
- Customer profile updates from CRM
- Marketing campaign results from CRM

Proposed future-state flow:

```text
ERP / CRM datasets
    → Scheduled AWS Glue ingestion
    → S3 Bronze raw zone
    → AWS Glue transformation
    → S3 Silver cleansed zone
    → S3 Gold analytics zone
```

Batch ingestion is appropriate when the data does not need second-by-second movement. It is often simpler, more cost-conscious, and easier to operate for large operational datasets.

---

## Data Lake Layers

The architecture follows a medallion-style design.

```text
Bronze → Silver → Gold
```

Each layer has a different purpose.

### Bronze Layer

The Bronze layer stores raw source-aligned data.

This data should remain close to the original source format so it can support auditability, replay, debugging, and backfills.

Example future-state prefixes:

```text
s3://retail-data-lake/bronze/pos/
s3://retail-data-lake/bronze/mobile/
s3://retail-data-lake/bronze/web/
s3://retail-data-lake/bronze/ecommerce/
s3://retail-data-lake/bronze/erp/
s3://retail-data-lake/bronze/crm/
```

Bronze data is usually not the best layer for business reporting because it may contain duplicates, inconsistent formats, missing values, raw PII, or source-specific field names.

### Silver Layer

The Silver layer stores cleaned, validated, standardized data.

Processing from Bronze to Silver may include:

- Required field validation
- Schema checks
- Type casting
- Deduplication
- PII masking or tokenization
- Standardized customer, product, store, and order identifiers
- Error routing for invalid records
- Metadata enrichment

Example future-state prefixes:

```text
s3://retail-data-lake/silver/retail_events/
s3://retail-data-lake/silver/orders/
s3://retail-data-lake/silver/customers/
s3://retail-data-lake/silver/inventory/
```

Silver data is more trustworthy than Bronze data and can be reused by downstream transformation jobs, analysts, and data science workloads.

### Gold Layer

The Gold layer stores business-ready datasets.

Gold datasets are shaped around reporting, KPIs, dashboards, and machine learning use cases.

Example future-state datasets:

```text
s3://retail-data-lake/gold/fact_sales/
s3://retail-data-lake/gold/dim_customer/
s3://retail-data-lake/gold/inventory_alerts/
s3://retail-data-lake/gold/customer_segments/
```

Gold data supports use cases such as:

- Store sales dashboards
- Inventory optimization
- Customer 360 reporting
- Marketing segmentation
- Abandoned-cart analysis
- Demand forecasting
- Executive KPI reporting

---

## Validation and Error Routing

Data quality checks help prevent bad source data from silently becoming trusted analytics data.

In the future-state architecture, validation can happen during movement from Bronze to Silver. This may be implemented with Lambda for lightweight event checks, AWS Glue for larger transformations, or dedicated data quality tools.

Typical validation checks include:

- Required fields are present
- Event types are supported
- Numeric fields contain valid values
- Sensitive fields are masked or tokenized
- Records follow expected schemas
- Duplicate records are detected
- Late or missing source data is identified

Invalid data should be routed to an error or quarantine area instead of being dropped.

```text
Invalid raw record
    → validation failure
    → error zone
    → operational review or reprocessing
```

This pattern allows valid records to continue through the pipeline while preserving invalid records for troubleshooting.

---

## Metadata and Lineage

A professional data platform needs to explain where data came from, how it was processed, and whether it passed quality checks.

Metadata can include:

| Metadata Field | Purpose |
|---|---|
| Source system | Identifies whether data came from POS, mobile, web, e-commerce, ERP, or CRM |
| Source bucket and key | Shows where the raw file landed |
| Processing timestamp | Shows when the record was processed |
| Validation status | Indicates whether the record was valid or invalid |
| Validation errors | Explains why a record failed quality checks |
| Pipeline layer | Identifies whether the record belongs to Bronze, Silver, Gold, or error output |
| Processor | Identifies the Lambda, Glue job, or transformation process that handled the data |

This supports data lineage, troubleshooting, auditability, and operational support.

---

## Governance and Security Flow

Retail data may include personally identifiable information and sensitive operational data.

Security and governance controls should apply throughout the data flow.

Recommended controls include:

- S3 bucket public access blocking
- Encryption at rest
- Least-privilege IAM roles
- Role-based access to Bronze, Silver, and Gold layers
- PII masking or tokenization before broad analytics use
- Glue Data Catalog metadata management
- CloudWatch logging
- Audit trails for data access and processing

The general access pattern is:

| Layer | Typical Access Pattern |
|---|---|
| Bronze | Restricted to data engineering, platform, and governance teams |
| Silver | Available to approved engineering, analytics, and data science users |
| Gold | Preferred layer for business reporting, dashboards, and executive analytics |
| Error zone | Restricted to teams responsible for troubleshooting and reprocessing |

This separation helps protect raw sensitive data while still enabling self-service analytics from curated datasets.

---

## Analytics and Consumption

Once data reaches Silver and Gold layers, it can be used by downstream analytics and machine learning tools.

Future-state consumption options include:

| Tool or Platform | Example Use |
|---|---|
| Athena | Serverless SQL queries over curated S3 data |
| QuickSight | Dashboards and self-service BI |
| SageMaker | Machine learning, forecasting, and customer segmentation |
| Redshift | AWS-native warehouse analytics |
| Snowflake | Optional warehouse layer for multi-team analytics and elastic compute |

The preferred reporting path is usually through Gold datasets because they contain the most business-ready definitions.

Example consumption flow:

```text
Gold sales and customer datasets
    → Athena or warehouse query layer
    → QuickSight dashboard
    → Business users
```

Example machine learning flow:

```text
Silver and Gold historical datasets
    → SageMaker or data science environment
    → Demand forecasting, recommendation, or segmentation model
```

---

## Proof-of-Concept Data Flow

The proof-of-concept in this repository implements a smaller working slice of the future-state design.

It does not deploy Kinesis, Glue, Athena, QuickSight, Redshift, Snowflake, SageMaker, ERP ingestion, CRM ingestion, or Gold datasets.

The implemented flow is:

```text
JSON file uploaded to raw S3 bucket under incoming/
    → S3 object-created notification
    → Lambda validator
    → Required field and event type validation
    → PII masking for email and phone fields
    → Metadata enrichment
    → Valid record written to curated bucket under silver/retail_events/
    → Invalid record written to curated bucket under errors/retail_events/
    → Processing activity logged to CloudWatch
```

This proof-of-concept demonstrates the Bronze-to-Silver validation pattern with error routing.

### Implemented AWS Resources

The Terraform proof-of-concept deploys:

| Resource | Purpose |
|---|---|
| Raw S3 bucket | Receives source JSON files |
| Curated S3 bucket | Stores valid Silver outputs and invalid error outputs |
| Lambda function | Validates, masks, enriches, and routes records |
| IAM role and policy | Allows Lambda to read raw data, write curated data, and log activity |
| S3 event notification | Invokes Lambda when JSON files are uploaded under `incoming/` |
| CloudWatch logs | Stores Lambda processing logs |

### Implemented Event Types

The Lambda validator currently supports:

| Event Type | Meaning |
|---|---|
| `pos_transaction` | In-store point-of-sale transaction |
| `ecommerce_order` | Online order from the e-commerce platform |
| `app_click` | Mobile or web application interaction event |

These event types represent a small subset of the full source landscape. ERP and CRM ingestion are part of the future-state design, but they are not implemented in the lightweight proof-of-concept.

### Implemented Validation Rules

Each event must include:

| Field | Purpose |
|---|---|
| `event_id` | Unique identifier for the event |
| `event_type` | Describes the type of retail event |
| `customer_id` | Connects the event to a customer profile |
| `event_timestamp` | Indicates when the event occurred |

The Lambda also checks that `transaction_total` and `cart_total` are numeric and non-negative when those fields are present.

### Implemented Output Routing

Valid records are written to:

```text
silver/retail_events/
```

Invalid records are written to:

```text
errors/retail_events/
```

Although both prefixes are stored in the curated S3 bucket for the proof-of-concept, they represent different logical outcomes:

- `silver/retail_events/` contains records that passed validation
- `errors/retail_events/` contains records that failed validation and need review

---

## Future-State vs Proof-of-Concept

The table below separates the complete proposed architecture from what is actually deployed in this repository.

| Capability | Future-State Architecture | Proof-of-Concept Implementation |
|---|---|---|
| POS data | Near real-time ingestion into Bronze | Represented by sample JSON event files |
| Mobile/web data | Near real-time event ingestion | Represented by supported `app_click` event type |
| E-commerce data | Near real-time or micro-batch ingestion | Represented by sample JSON event files |
| ERP data | Scheduled batch ingestion with Glue | Documented only |
| CRM data | Scheduled batch ingestion with Glue | Documented only |
| Bronze layer | Raw S3 zones by source | Raw S3 bucket with `incoming/` prefix |
| Silver layer | Cleaned and standardized S3 datasets | Curated S3 bucket with `silver/retail_events/` prefix |
| Gold layer | Business-ready analytics datasets | Documented only |
| Validation | Lambda, Glue, or data quality tools | Lambda validation rules |
| PII protection | Masking, tokenization, access control | Email and phone masking in Lambda |
| Error handling | Quarantine/error zone, alerts, reprocessing | `errors/retail_events/` prefix |
| Metadata catalog | Glue Data Catalog | Documented only |
| Analytics | Athena, QuickSight, Redshift, Snowflake | Documented only |
| Machine learning | SageMaker over curated data | Documented only |
| Monitoring | CloudWatch, alarms, dashboards | CloudWatch logs |

---

## Example End-to-End Scenario

The following example shows how the future-state design would support a business use case.

### Store Sales and Inventory Visibility

1. A customer buys an item in a physical store.
2. The POS system emits a `pos_transaction` event.
3. The event is ingested through the near real-time ingestion path.
4. The raw event lands in the Bronze POS zone.
5. Validation checks confirm that required fields are present and values are valid.
6. Sensitive customer fields are masked or tokenized.
7. The cleaned record is written to the Silver retail events dataset.
8. The transaction is combined with ERP inventory data.
9. Gold datasets update sales and inventory metrics.
10. Business users view updated store performance and inventory dashboards.

This scenario shows why multiple source systems matter. POS data explains the sale, ERP data explains inventory position, and curated Gold datasets make the combined information usable for business decisions.

---

## Key Takeaway

The proposed solution is an end-to-end retail data lake architecture that centralizes data from POS, mobile, web, e-commerce, ERP, and CRM systems.

The proof-of-concept intentionally implements only one focused slice:

```text
Raw S3 upload
    → Lambda validation and PII masking
    → Silver or error S3 output
    → CloudWatch logs
```

This slice is small, but it demonstrates an important production pattern: raw data should be validated, protected, enriched with metadata, and routed intentionally before it becomes trusted analytics data.
.
