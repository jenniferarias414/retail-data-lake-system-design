"""
Retail Event Validator Lambda

This Lambda function represents a lightweight proof-of-concept for the
Retail Data Lake System Design project.

Purpose:
- Read raw retail event JSON files from an S3 raw zone
- Validate required event fields
- Mask basic PII fields before curated storage
- Add pipeline metadata
- Write valid records to a curated/silver prefix
- Write invalid records to an error prefix
- Log processing activity for operational visibility

Expected flow:
S3 raw upload -> Lambda -> S3 curated/error output
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List
from urllib.parse import unquote_plus

import boto3


s3_client = boto3.client("s3")


REQUIRED_FIELDS = [
    "event_id",
    "event_type",
    "customer_id",
    "event_timestamp",
]


SUPPORTED_EVENT_TYPES = {
    "pos_transaction",
    "ecommerce_order",
    "app_click",
}


def mask_email(email: str) -> str:
    """Mask an email address while preserving the domain for debugging."""
    if not isinstance(email, str) or "@" not in email:
        return email

    local_part, domain = email.split("@", 1)

    if len(local_part) <= 2:
        masked_local = local_part[0] + "*" if local_part else "*"
    else:
        masked_local = f"{local_part[0]}{'*' * (len(local_part) - 2)}{local_part[-1]}"

    return f"{masked_local}@{domain}"


def mask_phone(phone: str) -> str:
    """Mask a phone number while preserving the last four digits."""
    if not isinstance(phone, str):
        return phone

    digits = [char for char in phone if char.isdigit()]

    if len(digits) < 4:
        return "***"

    return f"***-***-{''.join(digits[-4:])}"


def validate_event(event_record: Dict[str, Any]) -> List[str]:
    """Return a list of validation errors for a retail event."""
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in event_record or event_record[field] in [None, ""]:
            errors.append(f"Missing required field: {field}")

    event_type = event_record.get("event_type")
    if event_type and event_type not in SUPPORTED_EVENT_TYPES:
        errors.append(f"Unsupported event_type: {event_type}")

    if "transaction_total" in event_record:
        try:
            if float(event_record["transaction_total"]) < 0:
                errors.append("transaction_total cannot be negative")
        except (TypeError, ValueError):
            errors.append("transaction_total must be numeric")

    if "cart_total" in event_record:
        try:
            if float(event_record["cart_total"]) < 0:
                errors.append("cart_total cannot be negative")
        except (TypeError, ValueError):
            errors.append("cart_total must be numeric")

    return errors


def add_metadata(
    event_record: Dict[str, Any],
    source_bucket: str,
    source_key: str,
    validation_status: str,
    validation_errors: List[str],
) -> Dict[str, Any]:
    """Add standard data pipeline metadata to the event."""
    enriched_record = event_record.copy()

    if "email" in enriched_record:
        enriched_record["email"] = mask_email(enriched_record["email"])

    if "phone" in enriched_record:
        enriched_record["phone"] = mask_phone(enriched_record["phone"])

    enriched_record["_metadata"] = {
        "validation_status": validation_status,
        "validation_errors": validation_errors,
        "pipeline_layer": "silver" if validation_status == "valid" else "error",
        "source_bucket": source_bucket,
        "source_key": source_key,
        "processed_at": datetime.now(timezone.utc).isoformat(),
        "processor": "validate_retail_event_lambda",
    }

    return enriched_record


def build_output_key(source_key: str, validation_status: str) -> str:
    """Build the curated or error output key based on validation status."""
    filename = source_key.split("/")[-1]

    if validation_status == "valid":
        return f"silver/retail_events/{filename}"

    return f"errors/retail_events/{filename}"


def process_s3_object(source_bucket: str, source_key: str, target_bucket: str) -> Dict[str, Any]:
    """Read, validate, enrich, and write one S3 object."""
    print(f"Reading object from s3://{source_bucket}/{source_key}")

    response = s3_client.get_object(Bucket=source_bucket, Key=source_key)
    raw_body = response["Body"].read().decode("utf-8")
    event_record = json.loads(raw_body)

    validation_errors = validate_event(event_record)
    validation_status = "valid" if not validation_errors else "invalid"

    output_record = add_metadata(
        event_record=event_record,
        source_bucket=source_bucket,
        source_key=source_key,
        validation_status=validation_status,
        validation_errors=validation_errors,
    )

    output_key = build_output_key(source_key, validation_status)

    s3_client.put_object(
        Bucket=target_bucket,
        Key=output_key,
        Body=json.dumps(output_record, indent=2),
        ContentType="application/json",
    )

    print(
        json.dumps(
            {
                "source_bucket": source_bucket,
                "source_key": source_key,
                "target_bucket": target_bucket,
                "output_key": output_key,
                "validation_status": validation_status,
                "validation_errors": validation_errors,
            }
        )
    )

    return {
        "source_key": source_key,
        "output_key": output_key,
        "validation_status": validation_status,
        "validation_errors": validation_errors,
    }


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda entry point for S3 event notifications."""
    target_bucket = os.environ["CURATED_BUCKET_NAME"]

    results = []

    for record in event.get("Records", []):
        source_bucket = record["s3"]["bucket"]["name"]
        source_key = unquote_plus(record["s3"]["object"]["key"])

        result = process_s3_object(
            source_bucket=source_bucket,
            source_key=source_key,
            target_bucket=target_bucket,
        )

        results.append(result)

    return {
        "statusCode": 200,
        "processed_records": len(results),
        "results": results,
    }


if __name__ == "__main__":
    print("This module is designed to run as an AWS Lambda function.")