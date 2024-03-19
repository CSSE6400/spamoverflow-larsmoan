from flask import Blueprint, jsonify, request
import subprocess
import shortuuid
import json
from spamoverflow.models.spamoverflow import Email, Domain, Customer
from utils.utils import find_domains, validate_content_json
from spamoverflow.models import db
from spamoverflow import cache
from sqlalchemy import func
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/')
def home():
    return "Welcome to Lars's spamoverflow api"

@api.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

#Get info about a specific email from a specific customer
@api.route('/customers/<string:customer_id>/emails/<string:id>', methods=['GET'])
def get_email(customer_id: str, id: str):
    print(customer_id, id)
    email = Email.query.filter(Email.customer_id == customer_id, Email.id == id).first()
    if not email:
        return jsonify({"Error": f"Could not find an entry in the database for customer_id: {customer_id} and email_id: {id}"}), 404
    try:
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
                "spamhammer": email.spamhammer_metadata
            }
        }
        return response, 200
    except Exception as e:
        return jsonify({str(e)}), 500


@api.route('/customers/<string:customer_id>/emails', methods=['GET'])
def get_emails(customer_id: str):
    #Should return a list of all submitted emails for a given customer
    try:
        emails = Email.query.filter(Email.customer_id == customer_id).all()
        if type(customer_id) != str:
            return jsonify({"Eroor": "customer id is of the wrong type"}), 400
        return_list = []
        for email in emails:
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
                    "spamhammer": email.spamhammer_metadata
                }
            }
            return_list.append(response)
        return return_list, 200
    except subprocess.CalledProcessError as e:
        error_message = f"Unknow error when fetching emails for a given customer: {str(e)}"
        return jsonify({"error": error_message}), 500 


# Scan request for an email
@api.route('/customers/<string:customer_id>/emails', methods=['POST'])
def scan_request(customer_id: str):
    email_id = shortuuid.uuid() #Id created for that specific email

    #Extract if the customer is of high priority or not, for now we simply add the priority to the database
    priority = False
    if customer_id[:4] == "1111":
        priority = True

    contents = request.json
    spamhammer_metadata = contents.get("metadata").get("spamhammer")
    body = contents.get("contents").get("body")

    valid, e = validate_content_json(contents)  
    if not valid:
        return jsonify({"error": e.message}), 401   #If the body doesn't match the predefined schema, return the error

    email = Email(
        id = email_id,
        customer_id = customer_id,
        priority = priority,
        subject = contents.get("contents").get("subject"),
        from_id = contents.get("contents").get("from"),
        to_id = contents.get("contents").get("to"),
        spamhammer_metadata = spamhammer_metadata,
        body = body
    )
    db.session.add(email)
    #If the customer_id is not present in the database, create a new entry
    existing_customer = Customer.query.filter_by(id=customer_id).first()
    if not existing_customer:
        customer = Customer(id = customer_id)
        db.session.add(customer)
        db.session.commit()

    domains = find_domains(body)  #Extracts all the links from the body of the email

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


@api.route('/customers/<string:customer_id>/reports/domains', methods=['GET'])
@cache.cached(timeout=10)  # Cache this route for 300 secs (5min)
def get_domains(customer_id: str):
    malicious_domains = (
        db.session.query(Domain.link, db.func.count())
        .join(Email)
        .filter(Email.customer_id == customer_id, Email.malicious == True)
        .group_by(Domain.link)
        .all()
    )
    generated_at = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    data = []
    for domain, count in malicious_domains:
        data.append({
            "id": domain,
            "count": count
        })
    response = {
        "generated_at": generated_at,
        "total": len(malicious_domains),
        "data": data
    }
    return jsonify(response), 200

@api.route('/customers/<customer_id>/reports/actors')
@cache.cached(timeout=30)  # Cache this route for 300 secs (5min)
def get_malicious_senders(customer_id: str):
    # Query the database to get malicious senders for the specified customer_id
    malicious_senders = (
        db.session.query(Email.from_id, func.count())
        .filter(Email.customer_id == customer_id, Email.malicious == True)
        .group_by(Email.from_id)
        .all()
    )

    # Prepare the response data
    generated_at = datetime.utcnow()
    total = len(malicious_senders)
    data = [{"id": sender, "count": count} for sender, count in malicious_senders]

    response = {
        "generated_at": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": total,
        "data": data
    }

    return jsonify(response), 200


@api.route('/customers/<customer_id>/reports/recipients')
@cache.cached(timeout=30)  # Cache this route for 300 secs (5min)
def get_malicious_recipients(customer_id: str):
    # Query the database to get malicious senders for the specified customer_id
    recipients_malicious = (
        db.session.query(Email.to_id, func.count())
        .filter(Email.customer_id == customer_id, Email.malicious == True)
        .group_by(Email.to_id)
        .all()
    )

    # Prepare the response data
    generated_at = datetime.utcnow()
    total = len(recipients_malicious)
    data = [{"id": recipient, "count": count} for recipient, count in recipients_malicious]

    response = {
        "generated_at": generated_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": total,
        "data": data
    }

    return jsonify(response), 200