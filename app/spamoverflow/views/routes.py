from flask import Blueprint, jsonify, request
import subprocess
import shortuuid
import json
from spamoverflow.models.spamoverflow import Email 

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


@api.route('/customers/<string:customer_id>/emails', methods=['POST'])
def scan_request(customer_id: str):

    # 1: Add the email to the database if it is not present
    id = shortuuid.uuid()
    contents = request.json.get('contents')
    spamhammer_metadata = request.json.get("metadata").get("spamhammer")
    body = contents.get("body")

    email = Email(
        email_id = id,
        customer_id = customer_id,
        subject = contents.get("subject"),
        from_id = contents.get("from"),
        to_id = contents.get("to")
    )

    db.session.add(email)
    db.session.commit()
    
    spamhammer_input = {
        "id": id,
        "content": body,
        "metadata": spamhammer_metadata
    }
    print(spamhammer_input)

    try:
        # Specify the path to the SpamHammer binary
        binary_path = "./spamoverflow/spamhammer-v1.0.0-darwin-amd64"  # Update this with the actual path
    
        # Run the SpamHammer binary with any necessary arguments
        result = subprocess.run([binary_path, "scan"], input=json.dumps(spamhammer_input), capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)
        return output, 200

    except subprocess.CalledProcessError as e:
        # Handle the CalledProcessError
        error_message = f"Error trying to run spamhammer to scan an email: {str(e)}"
        return jsonify({"error": error_message}), 500  # Return a JSON response with the error message and status code 500
    
