# Data Quality Rules

## Purpose

This document defines the lightweight validation rules used in the retail data lake proof-of-concept.

In the future-state architecture, data quality checks would occur as data moves from the raw Bronze layer into the cleaned Silver layer. This proof-of-concept implements a small version of that pattern using AWS Lambda.

---

## Validation Scope

The proof-of-concept validates JSON retail event files uploaded to the raw S3 zone.

Supported event types:

- `pos_transaction`
- `ecommerce_order`
- `app_click`

---

## Required Fields

Each retail event must include:

| Field | Purpose |
|---|---|
| `event_id` | Unique identifier for the event |
| `event_type` | Describes the type of retail event |
| `customer_id` | Connects the event to a customer profile |
| `event_timestamp` | Indicates when the event occurred |

Records missing one or more required fields are routed to the error zone.

---

## Supported Event Types

The Lambda validator currently accepts:

| Event Type | Description |
|---|---|
| `pos_transaction` | In-store point-of-sale transaction |
| `ecommerce_order` | Online order from the e-commerce platform |
| `app_click` | Mobile or web application interaction event |

Unsupported event types are routed to the error zone.

---

## Numeric Field Validation

If present, these fields must be numeric and non-negative:

| Field | Example |
|---|---|
| `transaction_total` | POS transaction amount |
| `cart_total` | Online order/cart amount |

Negative or non-numeric values are treated as validation errors.

---

## PII Masking

Personally identifiable information is masked before records are written to the curated zone.

Masked fields:

| Field | Masking Approach |
|---|---|
| `email` | Preserves first and last character of username and keeps domain |
| `phone` | Preserves only the last four digits |

Example:

```json
{
  "email": "customer@example.com",
  "phone": "555-123-4567"
}
```

becomes:

```json
{
  "email": "c******r@example.com",
  "phone": "***-***-4567"
}
```

---

## Metadata Added During Processing

Each processed record includes a `_metadata` object.

Example metadata fields:

| Field | Purpose |
|---|---|
| `validation_status` | Indicates whether the record is valid or invalid |
| `validation_errors` | Lists validation issues if any exist |
| `pipeline_layer` | Indicates whether the record moved to `silver` or `error` |
| `source_bucket` | Original S3 bucket |
| `source_key` | Original S3 object path |
| `processed_at` | Timestamp when the Lambda processed the event |
| `processor` | Name of the processing component |

---

## Output Routing

Valid records are written to:

```text
silver/retail_events/
```

Invalid records are written to:

```text
errors/retail_events/
```

This routing pattern supports operational review of bad records without blocking valid events from moving forward.

---

## Future Enhancements

In a production implementation, data quality could be expanded with:

- Schema registry or event contracts
- Duplicate event detection
- Null threshold checks
- Referential integrity checks
- Freshness checks
- Row count reconciliation
- Automated alerts for quality failures
- Great Expectations, Deequ, dbt tests, or Glue Data Quality