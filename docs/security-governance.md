# Security and Governance Plan

## Purpose

This document describes the security and governance considerations for the Retail Data Lake System Design project.

XYZ Retail handles customer and transaction data across physical stores, mobile applications, web commerce, ERP systems, and CRM systems. Because this data may include personally identifiable information, the architecture must protect sensitive fields, control access, and provide auditability.

---

## Sensitive Data Considerations

Retail systems may contain personally identifiable information and sensitive business data.

Examples include:

| Data Element | Sensitivity |
|---|---|
| Customer name | Personally identifiable information |
| Email address | Personally identifiable information |
| Phone number | Personally identifiable information |
| Mailing address | Personally identifiable information |
| Customer ID | Identifier that may link to customer profile |
| Payment method | Sensitive transaction-related data |
| Store transaction data | Business-sensitive operational data |
| Marketing engagement | Customer behavior data |
| Inventory levels | Business-sensitive operational data |

The proof-of-concept includes email and phone fields to demonstrate basic masking before curated storage.

---

## Security Goals

The architecture should support these security goals:

- Protect customer data
- Restrict access by role and business need
- Encrypt data at rest and in transit
- Separate raw, curated, and error data zones
- Mask or tokenize PII where appropriate
- Maintain audit logs for processing and access
- Prevent public access to S3 buckets
- Support compliance requirements across business units

---

## Access Control

### IAM Role-Based Access

AWS Identity and Access Management should be used to control which services and users can access data.

Access should follow the principle of least privilege.

Example access patterns:

| Role | Example Access |
|---|---|
| Data ingestion role | Write to Bronze/raw zone |
| ETL processing role | Read Bronze, write Silver and Gold |
| Analyst role | Read curated Gold datasets |
| Data scientist role | Read approved Silver/Gold datasets |
| Security/admin role | Review audit logs and access policies |

### Proof-of-Concept Access

The proof-of-concept Lambda role is intentionally scoped to:

- Read objects from the raw S3 bucket
- Write objects to the curated S3 bucket
- Write logs to CloudWatch

The Lambda does not receive broad administrative permissions.

---

## S3 Security Controls

### Block Public Access

All S3 buckets in the proof-of-concept use public access blocking.

This prevents accidental public exposure of raw or curated retail data.

### Encryption at Rest

S3 buckets are configured with server-side encryption using AES-256.

In a production implementation, customer-managed AWS KMS keys could be used for stronger key management and audit controls.

### Bucket Separation

The architecture separates data by purpose:

```text
Raw / Bronze zone
Curated / Silver zone
Gold analytics zone
Error records zone
```

This separation supports cleaner access control, lifecycle management, and troubleshooting.

---

## PII Masking

### Proof-of-Concept Masking

The Lambda validator masks email and phone fields before writing records to the curated zone.

Example raw values:

```json
{
  "email": "customer@example.com",
  "phone": "555-123-4567"
}
```

Example curated values:

```json
{
  "email": "c******r@example.com",
  "phone": "***-***-4567"
}
```

### Why Masking Matters

Masking reduces exposure of sensitive customer data in downstream analytics layers.

Business users often do not need full email addresses or phone numbers to analyze sales, inventory, or customer behavior trends.

### Production Considerations

In a production implementation, masking could be expanded with:

- Tokenization
- Hashing
- Column-level access controls
- Row-level security
- Dynamic masking in Snowflake or warehouse layer
- Separate secure storage for sensitive fields
- Data classification tags

---

## Data Catalog and Metadata Governance

The full architecture recommends using Glue Data Catalog for metadata management.

A data catalog helps teams understand:

- What datasets exist
- Where data is stored
- What schema each dataset uses
- Who owns the dataset
- Which fields contain sensitive data
- How data flows from source to consumption

In production, the catalog should include business and technical metadata.

Examples:

| Metadata Type | Example |
|---|---|
| Technical schema | Column names and data types |
| Source metadata | POS, ERP, CRM, web, app |
| Sensitivity tags | PII, internal, public, restricted |
| Ownership | Sales analytics, marketing, inventory, finance |
| Freshness expectations | Hourly, daily, near real-time |

---

## Auditability

The architecture should support auditability across ingestion, transformation, and access.

Recommended audit signals:

- Who accessed sensitive datasets
- When files arrived in the raw zone
- Which process transformed the record
- Which validation rules passed or failed
- Which records were routed to errors
- Which IAM roles accessed each bucket
- Which dashboards or downstream systems consumed the data

The proof-of-concept adds processing metadata to each output record and logs processing activity in CloudWatch.

---

## Error Handling and Quarantine

Invalid records should not silently disappear or block all processing.

The architecture routes invalid records to an error zone.

```text
Invalid event → errors/retail_events/
```

This pattern supports:

- Troubleshooting
- Manual review
- Reprocessing
- Source system feedback
- Data quality monitoring

In production, invalid record handling could be expanded with alerts, dashboards, and automatic ticket creation.

---

## Governance by Data Layer

### Bronze Layer

The Bronze layer contains raw source-aligned data.

Access should be restricted because raw data may include unmasked PII or messy source values.

Recommended access:

- Data engineering team
- Platform team
- Security/governance team

### Silver Layer

The Silver layer contains cleaned and standardized data.

Sensitive fields should be masked, tokenized, or access-controlled before broader use.

Recommended access:

- Data engineering team
- Approved analysts
- Data scientists
- Downstream transformation jobs

### Gold Layer

The Gold layer contains business-ready datasets.

This is the preferred layer for most reporting and dashboard users.

Recommended access:

- Business analysts
- Inventory managers
- Marketing analysts
- Executives
- BI tools

---

## Monitoring and Alerting

Security and governance require ongoing monitoring.

Recommended monitoring includes:

- Failed Lambda executions
- Glue job failures
- Unexpected schema changes
- High error-record counts
- Access denied events
- Unusual data access patterns
- Public access configuration drift
- Missing or late-arriving data
- PII appearing in unauthorized layers

The proof-of-concept uses CloudWatch logs to verify Lambda processing and validation output.

---

## Compliance Considerations

The business requirement specifically identifies PII such as email, phone, and address.

A production architecture should support compliance controls such as:

- Encryption
- Masking
- Audit trails
- Access reviews
- Retention policies
- Deletion or archival policies
- Data classification
- Least-privilege IAM
- Separation of duties

Specific compliance requirements would depend on the company, geography, and applicable regulations.

---

## Key Security Design Choices

| Area | Design Choice |
|---|---|
| Storage | S3 buckets with public access blocked |
| Encryption | Server-side encryption enabled |
| Access | IAM roles and least-privilege service permissions |
| PII | Masking before curated storage |
| Errors | Invalid records routed to an error prefix |
| Logs | CloudWatch logs for processing visibility |
| Metadata | Glue Data Catalog recommended for production |
| Governance | Bronze/Silver/Gold layer separation |

---

## Key Takeaway

Security and governance are not separate from data architecture. They are part of the design.

For XYZ Retail, the architecture must protect customer data while still enabling analytics, reporting, and machine learning. The proposed design supports this by separating raw and curated layers, applying PII masking, controlling access with IAM, encrypting storage, and preserving logs and metadata for auditability.