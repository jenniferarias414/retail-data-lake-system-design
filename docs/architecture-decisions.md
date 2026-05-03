# Architecture Decisions

## Purpose

This document explains the major architecture decisions made for the Retail Data Lake System Design project.

The goal is to show not only what was selected, but why it was selected, what alternatives were considered, and what tradeoffs come with each decision.

---

## Decision 1: Use Amazon S3 as the Central Data Lake Foundation

### Decision

Use Amazon S3 as the centralized storage layer for raw, cleaned, curated, and error-routed data.

### Why This Was Chosen

XYZ Retail needs to consolidate data from multiple systems, including point-of-sale systems, mobile/web applications, e-commerce, ERP, and CRM platforms.

Amazon S3 is a strong foundation because it can store large volumes of structured, semi-structured, and unstructured data at low cost. It also integrates well with AWS analytics and machine learning services such as Glue, Athena, Redshift, QuickSight, and SageMaker.

### Benefits

- Scales as data volume grows
- Supports many file formats such as JSON, CSV, Parquet, and logs
- Provides durable raw storage for replay and backfills
- Integrates with AWS data and analytics services
- Separates storage from compute
- Supports lifecycle policies for cost control

### Tradeoffs

- S3 by itself is not a database or warehouse
- Data can become difficult to manage without clear structure
- Query performance depends on file format, partitioning, and table design
- Governance and cataloging must be intentionally designed

### Mitigation

The architecture uses Bronze, Silver, and Gold zones to organize data by quality level. Glue Data Catalog, naming standards, partitioning, and access controls help prevent the data lake from becoming disorganized.

---

## Decision 2: Use Bronze, Silver, and Gold Data Layers

### Decision

Use a medallion-style architecture with Bronze, Silver, and Gold layers.

```text
Bronze = raw/source-aligned data
Silver = cleaned and standardized data
Gold = business-ready analytics data
```

### Why This Was Chosen

XYZ Retail has multiple source systems with different formats, freshness needs, and business definitions. Separating data into quality layers makes the platform easier to understand, troubleshoot, govern, and scale.

### Benefits

- Preserves raw source data for replay and audit
- Separates ingestion from transformation
- Allows validation and cleaning before analytics use
- Reduces inconsistent business metrics
- Supports downstream BI and machine learning use cases
- Makes data lineage easier to explain

### Tradeoffs

- Adds more data layers to manage
- Requires naming standards and documentation
- Can duplicate storage if not managed carefully
- Requires clear ownership of each layer

### Mitigation

Each layer has a clear purpose:

- Bronze stores raw source-aligned data
- Silver stores validated and standardized data
- Gold stores curated, business-ready datasets

Lifecycle policies and storage format choices can help manage cost.

---

## Decision 3: Use Separate Ingestion Patterns for Real-Time and Batch Sources

### Decision

Use near real-time ingestion for POS, mobile app, web, and e-commerce event data. Use batch ingestion for ERP and CRM datasets.

### Why This Was Chosen

Not all data sources require the same freshness.

Point-of-sale, app, web, and e-commerce events support use cases such as abandoned-cart recovery, near real-time inventory alerts, and store performance monitoring. These use cases benefit from faster ingestion.

ERP and CRM data often supports operational reporting, customer profiles, finance, procurement, and marketing analysis. These datasets can usually be processed on a schedule.

### Benefits

- Applies the right pattern to each source type
- Avoids overengineering batch workloads as streaming
- Improves freshness for high-value event data
- Keeps operational datasets simpler and cost-conscious

### Tradeoffs

- Multiple ingestion patterns increase complexity
- Monitoring must cover both event-driven and scheduled pipelines
- Different teams may own different data sources

### Mitigation

The architecture standardizes all source data into S3 Bronze/Silver/Gold zones, even if ingestion patterns differ. Centralized logging, metadata cataloging, and consistent documentation help keep the design maintainable.

---

## Decision 4: Use AWS Lambda for a Lightweight Proof-of-Concept

### Decision

Use AWS Lambda in the proof-of-concept to validate raw retail event files, mask PII fields, add metadata, and route outputs to curated or error prefixes.

### Why This Was Chosen

The full architecture would require multiple services such as Kinesis, Glue, Athena, QuickSight, Redshift, or Snowflake. Deploying all of those services for a small assignment would add unnecessary cost and complexity.

Lambda provides a small, serverless way to demonstrate one important data engineering pattern:

```text
Raw S3 event → validation → PII masking → curated/error S3 output
```

### Benefits

- Low operational overhead
- Event-driven
- Cost-conscious for small volumes
- Easy to connect to S3 object-created events
- Good for lightweight validation and routing
- Provides hands-on AWS proof without deploying the entire platform

### Tradeoffs

- Not suitable for large files or heavy transformations
- Runtime and memory limits apply
- Not a replacement for Glue, Spark, dbt, Redshift, or Snowflake transformations
- Needs careful error handling in production

### Mitigation

The project clearly scopes Lambda as a proof-of-concept validation component. Production-scale transformations would use Glue, Spark, dbt, Redshift, or Snowflake depending on the platform.

---

## Decision 5: Use AWS Glue for Production-Scale Batch Processing

### Decision

Recommend AWS Glue for production batch ingestion and transformation of ERP, CRM, and other large datasets.

### Why This Was Chosen

AWS Glue is a managed serverless ETL service that integrates with S3 and the Glue Data Catalog. It is appropriate for larger transformations that are beyond Lambda's intended use.

### Benefits

- Serverless Spark execution
- Handles larger datasets than Lambda
- Supports schema discovery with crawlers
- Integrates with S3, Athena, Redshift, and other AWS services
- Supports scheduled jobs and workflows
- Useful for transforming raw data into curated Parquet datasets

### Tradeoffs

- More expensive than Lambda for very small jobs
- Startup time can be slower than simple serverless functions
- Requires Spark/PySpark understanding for code-based jobs
- Needs monitoring and job tuning for production workloads

### Mitigation

Use Glue for workloads that justify distributed processing. Keep small event validation and routing logic in Lambda where appropriate.

---

## Decision 6: Use Kinesis Firehose or API Gateway for Near Real-Time Event Ingestion

### Decision

Recommend Kinesis Firehose or API Gateway for near real-time ingestion from POS, app, web, and e-commerce event sources.

### Why This Was Chosen

XYZ Retail needs faster insight into sales and customer behavior. Event-driven ingestion supports lower-latency use cases compared with overnight batch ETL.

### Benefits

- Supports near real-time event delivery
- Reduces report latency
- Helps with abandoned-cart recovery and inventory alerting
- Can land event data into S3 for downstream processing
- Decouples event producers from downstream analytics systems

### Tradeoffs

- Streaming/event architectures are more complex than batch pipelines
- Ordering, retries, and duplicate handling must be considered
- Costs can increase with continuous event volume
- Schema changes can break downstream processing if not managed

### Mitigation

Start with critical real-time use cases only. Use S3 as a durable landing zone, define event schemas, monitor failures, and route bad events separately.

---

## Decision 7: Use Athena and QuickSight for Self-Service Analytics

### Decision

Recommend Athena for SQL querying over curated S3 data and QuickSight for dashboarding.

### Why This Was Chosen

Business analysts, inventory managers, marketing analysts, and executives need access to trusted data without relying on custom extracts for every report.

Athena and QuickSight provide a serverless analytics path over curated datasets.

### Benefits

- No dedicated query cluster required
- Analysts can query curated S3 data with SQL
- QuickSight can provide dashboards for business users
- Works well with Glue Data Catalog
- Cost-conscious for moderate query workloads

### Tradeoffs

- Athena performance depends heavily on data layout
- Query costs can grow if users scan large raw datasets
- QuickSight setup and governance require planning
- For complex analytics, a dedicated warehouse may perform better

### Mitigation

Expose curated Gold datasets rather than raw data to most analysts. Use Parquet, compression, partitioning, and clear table design to reduce scan cost and improve performance.

---

## Decision 8: Support Redshift or Snowflake as Optional Warehouse Layer

### Decision

Design the architecture so that curated data can be consumed by Athena directly from S3 or loaded into Redshift/Snowflake depending on platform requirements.

### Why This Was Chosen

The assignment allows AWS or Snowflake. In real organizations, warehouse selection depends on existing standards, workload patterns, team skills, cost expectations, governance needs, and integration requirements.

### Benefits

- Keeps the architecture flexible
- Allows AWS-native teams to use Redshift
- Allows multi-team or low-ops teams to use Snowflake
- Keeps S3 as the central lake foundation regardless of warehouse choice

### Tradeoffs

- Supporting multiple warehouse options can add complexity
- Data modeling and orchestration may differ by platform
- Costs vary by warehouse usage patterns
- Security and governance models differ between platforms

### Mitigation

Use S3 as the durable data lake foundation and keep warehouse loading as a serving-layer decision. Document platform tradeoffs separately in `architecture/platform-decision.md`.

---

## Decision 9: Use Terraform for the Proof-of-Concept Infrastructure

### Decision

Use Terraform to create the proof-of-concept AWS resources.

### Why This Was Chosen

Terraform makes the infrastructure repeatable, reviewable, and easy to clean up after testing.

Instead of manually clicking through the AWS Console, the infrastructure is defined as code.

### Benefits

- Repeatable deployment
- Easier cleanup with `terraform destroy`
- Version-controlled infrastructure
- Shows cloud engineering and infrastructure-as-code practices
- Reduces manual setup steps

### Tradeoffs

- Requires local AWS credentials
- Requires Terraform installation
- Adds another language/tool to understand
- State files must be handled carefully and not committed

### Mitigation

The repo includes `.gitignore` entries to avoid committing local state, provider caches, generated zip files, and local outputs.

---

## Decision 10: Keep the Proof-of-Concept Small

### Decision

Deploy only a focused S3 + Lambda + CloudWatch proof-of-concept instead of deploying the entire production architecture.

### Why This Was Chosen

The full architecture includes services that may add setup time and cost, such as Glue, Athena, QuickSight, Kinesis, Redshift, Snowflake, or SageMaker.

The project goal is to demonstrate system design reasoning and one working AWS slice, not to create a full production retail platform.

### Benefits

- Keeps cost low
- Allows fast testing and screenshots
- Demonstrates a real serverless data pattern
- Avoids unnecessary complexity
- Supports portfolio-friendly proof without overbuilding

### Tradeoffs

- Does not prove full production scale
- Does not deploy Glue, Athena, QuickSight, Kinesis, Redshift, or Snowflake
- Does not include full orchestration or end-user dashboards

### Mitigation

The README and docs clearly distinguish between the full future-state architecture and the lightweight proof-of-concept. The proof-of-concept is positioned as an implementation slice, not the entire platform.

---

## Key Takeaway

The architecture decisions prioritize practical system design tradeoffs:

- Use S3 as the durable lake foundation
- Use different ingestion patterns for different source needs
- Use Bronze/Silver/Gold layers to manage data quality
- Use managed AWS services for scalability and operational simplicity
- Protect PII through masking, encryption, access control, and auditability
- Keep the proof-of-concept small enough to deploy safely and cheaply

This design balances business value, technical feasibility, cost control, and implementation readiness.