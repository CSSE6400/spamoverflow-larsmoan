import re
import uuid


import jsonschema
from jsonschema import validate
from rfc3339_validator import validate_rfc3339


def find_domains(text: str):
    # Regular expression to find all domains in the text
    domain_regex = r"https?://([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,4}))"
    # Find all domains using regex
    domains = re.findall(domain_regex, text)
    unique_domains = set([domain for domain in domains])
    return list(unique_domains)


# Validates that the body sent follows the schema
def validate_content_json(content):
    schema = {
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {"spamhammer": {"type": "string"}},
                "required": ["spamhammer"],
            },
            "contents": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "from": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"},
                },
                "required": ["to", "from", "subject", "body"],
            },
        },
        "required": ["metadata", "contents"],
    }
    try:
        validate(content, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation failed: {e.message}")
        return False, e


def validate_request(customer_id, request):
    # Flask's inherent type checking for supported types
    limit = request.args.get("limit", 100, type=int)
    offset = request.args.get("offset", 0, type=int)  # Default to 0 if not provided
    start = request.args.get("start")
    end = request.args.get("end")
    from_email = request.args.get("from", type=str)
    to_email = request.args.get("to", type=str)
    state = request.args.get("state", type=str)
    only_malicious = request.args.get("only_malicious")

    # Validate customer_id as UUID
    try:
        uuid.UUID(customer_id)
    except ValueError:
        raise ValueError(f"Invalid customer id: {customer_id}")

    # Custom validation for ranges and formats
    if limit <= 0 or limit > 1000:
        raise ValueError("limit must be an integer between 1 and 1000")
    if offset < 0:
        raise ValueError("offset must be a non-negative integer")
    if start and not validate_rfc3339(start):
        raise ValueError("start must be in RFC3339 format")
    if end and not validate_rfc3339(end):
        raise ValueError("end must be in RFC3339 format")
    if from_email and ("@" not in from_email):
        raise ValueError("from must be a valid email address")
    if to_email and ("@" not in to_email):
        raise ValueError("to must be a valid email address")
    if state and (state not in ["pending", "scanned", "failed"]):
        raise ValueError("state must be one of 'pending', 'scanned', 'failed'")
    if only_malicious and (only_malicious.lower() not in ["true", "false"]):
        raise ValueError("only_malicious string is of incorrect format")
