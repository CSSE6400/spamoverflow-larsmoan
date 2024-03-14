import re
import jsonschema
from jsonschema import validate

def find_domains(text: str):
    # Regular expression to find all domains in the text
    domain_regex = r'(?:http[s]?://)?(?:www\.)?([a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,4}))'

    domains = re.findall(domain_regex, text)
    return domains

#Validates that the body sent follows the schema
def validate_content_json(content):
    schema = {
        "type": "object",
        "properties": {
            "metadata": {
                "type": "object",
                "properties": {
                    "spamhammer": {"type": "string"}
                },
                "required": ["spamhammer"]
            },
            "contents": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "from": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "from", "subject", "body"]
            }
        },
        "required": ["metadata", "contents"]
    }
    try:
        validate(content, schema=schema)
        return True, None
    except jsonschema.exceptions.ValidationError as e:
        print(f"Validation failed: {e.message}")
        return False, e
    
#For testing 
example_body = {
    "metadata": {
        "spamhammer": "1|14"
    },
    "contents": {
        "to": "no-reply@uq.edu.au",
        "from": "sender@example.com",
        "subject": "Example Subject",
        "body": "Example Body"
    }
}

if __name__ == "__main__":
    ret = validate_content_json(example_body)
    print(ret)