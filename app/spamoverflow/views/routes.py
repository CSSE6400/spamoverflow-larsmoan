from flask import Blueprint, jsonify, request
import subprocess
import shortuuid
import json
from spamoverflow.models.spamoverflow import Email, Domain, Customer
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
    email_id = shortuuid.uuid() #Id created for that specific email
    
    contents = request.json
    spamhammer_metadata = contents.get("metadata").get("spamhammer")
    body = contents.get("contents").get("body")

    valid, e = validate_content_json(contents)  
    if not valid:
        return jsonify({"error": e.message}), 401   #If the body doesn't match the predefined schema, return the error

    email = Email(
        id = email_id,
        customer_id = customer_id,
        subject = contents.get("contents").get("subject"),
        from_id = contents.get("contents").get("from"),
        to_id = contents.get("contents").get("to"),
        body = body
    )
    db.session.add(email)
    #If the customer_id is not present in the database, create a new entry
    existing_customer = Customer.query.filter_by(id=customer_id).first()
    if not existing_customer:
        customer = Customer(id = customer_id)
        db.session.add(customer)
        db.session.commit()

    domains = find_links(body)  #Extracts all the links from the body of the email

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
        binary_path = "./spamoverflow/spamhammer-v1.0.0-darwin-amd64"  # This needs to be defined dynamically when dockerized
    
        # Running the actual spamchecker from binary
        result = subprocess.run([binary_path, "scan"], input=json.dumps(spamhammer_input), capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)  # output format: {'id': '4J4TXfZjsetACLv59H7i8L', 'malicious': True}
        
        malicious = output.get("malicious")

        #Updating the values for the email in the db entry
        email.malicious = malicious
        email.status = "scanned"
        db.session.commit()

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
        error_message = f"Error trying to run spamhammer to scan an email: {str(e)}"
        return jsonify({"error": error_message}), 500 