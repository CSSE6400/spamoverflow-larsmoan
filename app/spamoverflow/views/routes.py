from flask import Blueprint, jsonify, request
import subprocess
import shortuuid
import json
from spamoverflow.models.spamoverflow import Email, Domain
from utils.utils import find_links, validate_content_json

from spamoverflow.models import db

api = Blueprint('api', __name__)


@api.route('/')
def home():
    return "Welcome to Lars's spamoverflow api"

@api.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


@api.route('/customers/<string:customer_id>/emails', methods=['GET'])
def get_emails(customer_id: str):
    return jsonify({"user": customer_id}), 200



# Scan request for an email
@api.route('/customers/<string:customer_id>/emails', methods=['POST'])
def scan_request(customer_id: str):
    # 1: Add the email to the database
    email_id = shortuuid.uuid()
    contents = request.json

    spamhammer_metadata = contents.get("metadata").get("spamhammer")
    body = contents.get("contents").get("body")

    valid, e = validate_content_json(contents)  
    if not valid:
        # Return the error message as JSON with status code 401 (Unauthorized)
        return jsonify({"error": e.message}), 401

    email = Email(
        id = email_id,
        customer_id = customer_id,
        subject = contents.get("contents").get("subject"),
        from_id = contents.get("contents").get("from"),
        to_id = contents.get("contents").get("to"),
        body = body
    )
    db.session.add(email)

    domains = find_links(body)
    for link in domains:
        domain = Domain(link=link)
        db.session.add(domain)
        email.domains.append(domain)
    
    db.session.commit()
    
    spamhammer_input = {
        "id": email_id,
        "content": body,
        "metadata": spamhammer_metadata
    }

    try:
        # Specify the path to the SpamHammer binary
        binary_path = "./spamoverflow/spamhammer-v1.0.0-darwin-amd64"  # Update this with the actual path
    
        # Run the SpamHammer binary with any necessary arguments
        result = subprocess.run([binary_path, "scan"], input=json.dumps(spamhammer_input), capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        # output format: {'id': '4J4TXfZjsetACLv59H7i8L', 'malicious': True}

        malicious = output.get("malicious")

        #Updating the values in the database
        email.malicious = malicious
        email.status = "scanned"
        db.session.commit()

        
        #domain_links = [domain.link for domain in email.domains]

        #Creating the API response
        response = {
            "id": email.id,
            "created_at": email.created_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "updated_at": email.updated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "contents": {
                "to": email.to_id,
                "from": email.from_id,
                "subject": email.subject
            },
            "status": email.status,
            "malicious": email.malicious,
            "domains": [domain.link for domain in email.domains],
            "metadata": {
                "spamhammer": spamhammer_metadata
            }
        }
        return response, 201

    except subprocess.CalledProcessError as e:
        # Handle the CalledProcessError
        error_message = f"Error trying to run spamhammer to scan an email: {str(e)}"
        return jsonify({"error": error_message}), 500  # Return a JSON response with the error message and status code 500
    
