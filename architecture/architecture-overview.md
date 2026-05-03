# Architecture Overview

## Purpose

This document describes the future-state architecture for XYZ Retail's cloud-based data lake.

The goal is to modernize fragmented retail data systems into a centralized, governed, scalable data platform that supports near real-time insights, batch analytics, self-service reporting, and machine learning workloads.

---

## Business Context

XYZ Retail operates across physical stores, mobile applications, web commerce, and internal business systems.

The company collects data from several major source systems:

- Point-of-sale systems from physical stores
- Mobile and web application events
- E-commerce order and customer activity
- Enterprise Resource Planning data for inventory, finance, procurement, and supply chain
- Customer Relationship Management data for marketing and customer engagement

Currently, these systems are siloed, causing delayed reporting, inconsistent metrics, duplicated storage, and compliance risks around personally identifiable information.

---

## High-Level Architecture

The proposed architecture uses Amazon S3 as the centralized data lake foundation.

Data is ingested from both near real-time and batch sources, stored in raw form, validated and transformed into curated layers, and exposed to analytics and machine learning consumers.

```text
Retail Source Systems
    → Ingestion Layer
    → S3 Bronze Raw Zone
    → Validation and Transformation
    → S3 Silver Clean Zone
    → Gold Analytics Layer
    → Athena / QuickSight / SageMaker / Redshift / Snowflake
```

---

## Source Systems

### Point-of-Sale Systems

Point-of-sale systems capture in-store transactions, purchases, refunds, payment methods, store locations, and customer interactions.

These events are high-value because they support store performance analytics, inventory alerting, and customer purchase behavior analysis.

### Mobile and Web Applications

Mobile and web applications capture customer behavior such as page views, clicks, cart activity, searches, and feature usage.

These events support abandoned-cart recovery, product analytics, customer segmentation, and marketing optimization.

### E-Commerce Platform

The e-commerce platform captures online orders, cart totals, checkout events, product engagement, and customer activity.

This data is important for combining online and in-store behavior into a 360-degree customer view.

### Enterprise Resource Planning System

The Enterprise Resource Planning system tracks operational data such as inventory, procurement, supply chain, finance, and vendor activity.

This data is usually batch-oriented and supports inventory optimization, procurement planning, and operational reporting.

### Customer Relationship Management System

The Customer Relationship Management system tracks customer profiles, leads, loyalty activity, campaigns, and marketing engagement.

This data supports customer segmentation, marketing analytics, and personalization use cases.

---

## Ingestion Layer

The architecture uses separate ingestion patterns based on source behavior and freshness requirements.

### Near Real-Time Ingestion

Near real-time sources include:

- Point-of-sale events
- Mobile application events
- Web behavior events
- E-commerce order events

Recommended services:

- Amazon API Gateway for managed API ingestion
- Amazon Kinesis Data Firehose for streaming delivery into the data lake
- AWS Lambda for lightweight validation, routing, and enrichment

These sources benefit from lower-latency ingestion because business teams need more timely visibility into customer behavior, transactions, and inventory activity.

### Batch Ingestion

Batch sources include:

- Enterprise Resource Planning datasets
- Customer Relationship Management datasets

Recommended services:

- AWS Glue for scheduled ingestion and transformation
- Amazon S3 for raw file landing
- Glue Data Catalog for metadata discovery

ERP and CRM data often arrives on a schedule and may not require second-by-second processing. Batch ingestion is simpler, cost-effective, and appropriate for operational datasets that refresh hourly or daily.

---

## Data Lake Storage Layers

The data lake follows a medallion-style architecture.

```text
Bronze → Silver → Gold
```

### Bronze Layer

The Bronze layer stores raw data as close to the source format as possible.

This layer supports:

- Replay
- Auditability
- Backfills
- Debugging
- Source traceability

Examples:

```text
s3://retail-data-lake/bronze/pos/
s3://retail-data-lake/bronze/ecommerce/
s3://retail-data-lake/bronze/erp/
s3://retail-data-lake/bronze/crm/
```

### Silver Layer

The Silver layer contains cleaned, validated, standardized data.

This layer supports:

- Schema enforcement
- Deduplication
- Type casting
- PII masking or tokenization
- Standardized customer and product identifiers
- Curated datasets for downstream processing

Examples:

```text
s3://retail-data-lake/silver/retail_events/
s3://retail-data-lake/silver/customers/
s3://retail-data-lake/silver/inventory/
```

### Gold Layer

The Gold layer contains business-ready datasets designed for analytics, reporting, and machine learning.

This layer supports:

- KPI reporting
- Fact and dimension tables
- Customer 360 analytics
- Inventory optimization
- Store performance dashboards
- Marketing segmentation

Examples:

```text
s3://retail-data-lake/gold/fact_sales/
s3://retail-data-lake/gold/dim_customer/
s3://retail-data-lake/gold/inventory_alerts/
s3://retail-data-lake/gold/customer_segments/
```

---

## Processing and Transformation

AWS Glue is recommended for large-scale batch transformations because it provides managed Spark execution, integrates with S3, and works with the Glue Data Catalog.

AWS Lambda is recommended only for lightweight event validation, routing, and enrichment. Lambda is not intended to replace Glue for large-scale transformations.

This project's proof-of-concept demonstrates a small Lambda-based validation slice:

```text
Raw S3 event file
    → Lambda validation and PII masking
    → Curated S3 output or error output
```

In a production implementation, heavier transformations would be handled by Glue, Spark, dbt, Redshift, Snowflake, or another transformation layer depending on platform choice.

---

## Analytics and Consumption Layer

The curated data can support multiple consumers.

### Business Analysts

Business analysts can use Athena or QuickSight to query curated datasets and build dashboards.

### Inventory Managers

Inventory managers can use Gold inventory datasets to monitor stock levels, identify replenishment needs, and improve store-level availability.

### Marketing Analysts

Marketing analysts can use customer and engagement datasets for segmentation, campaign analysis, and abandoned-cart recovery.

### Data Scientists

Data scientists can use curated Silver and Gold datasets in SageMaker or other machine learning platforms for customer segmentation, demand forecasting, and recommendation modeling.

### Executive Stakeholders

Executives can use trusted Gold-level dashboards for store performance, customer experience trends, and operational KPIs.

---

## Governance and Security

The architecture includes centralized governance controls to protect sensitive customer data and improve trust.

Recommended controls include:

- IAM role-based access control
- S3 bucket encryption
- PII masking or tokenization
- Glue Data Catalog metadata management
- CloudWatch logging
- Audit trails for data access and processing
- Separate raw, curated, and error zones
- Least-privilege access patterns

This is especially important because the business requirements include personally identifiable information such as email, phone number, and address.

---

## Monitoring and Operations

The architecture should include operational monitoring across ingestion, transformation, and consumption.

Recommended monitoring areas:

- File arrival and ingestion success
- Lambda execution errors
- Glue job failures
- Data quality failures
- Late-arriving data
- S3 object counts and data volume
- Athena query cost and performance
- Dashboard freshness
- PII handling and access auditing

In the proof-of-concept, CloudWatch logs are used to verify Lambda processing and validation output.

---

## Platform Options

The architecture can support multiple analytical platform choices.

### Amazon Athena

Athena is useful for serverless SQL queries directly over curated data in S3.

It is a strong fit for ad hoc analysis, lightweight reporting, and cost-conscious querying when data is properly partitioned and stored in efficient formats.

### Amazon Redshift

Redshift is useful when the company wants an AWS-native warehouse with predictable workloads, IAM/VPC alignment, and strong integration with S3 through Redshift Spectrum.

### Snowflake

Snowflake is useful when the company wants minimal operations, separate compute for multiple teams, spiky workload support, secure data sharing, and multi-cloud flexibility.

The final choice depends on organizational standards, workload patterns, cost model, security requirements, and team expertise.

---

## Proof-of-Concept Scope

The full production architecture would include services such as Kinesis, Glue, Athena, QuickSight, Redshift, Snowflake, and SageMaker.

To keep the project focused and cost-conscious, the proof-of-concept implements one small production-relevant slice:

```text
S3 Raw Bucket
    → S3 object-created event
    → Lambda Validator
    → S3 Curated Bucket
    → CloudWatch Logs
```

This demonstrates:

- Raw-to-curated data movement
- Serverless event processing
- Data quality validation
- PII masking
- Error routing
- Infrastructure-as-code deployment with Terraform

---

## Key Takeaway

The recommended architecture gives XYZ Retail a scalable and governed data platform that can support both near real-time and batch analytics.

By centralizing data in Amazon S3, separating data into Bronze, Silver, and Gold layers, and applying governance and validation controls, the company can reduce reporting latency, improve metric consistency, support self-service analytics, and enable future machine learning use cases.