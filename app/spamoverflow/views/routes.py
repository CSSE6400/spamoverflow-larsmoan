from flask import Blueprint, jsonify, request
import subprocess
import shortuuid
import json

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
    #The relevant content for spamhammer
    content = request.json.get('contents').get('body')    
    metadata = request.json.get('metadata').get('spamhammer')
    id = shortuuid.uuid()

    json_data = {
        "id": id,
        "content": content,
        "metadata": metadata
    }

    try:
        # Specify the path to the SpamHammer binary
        binary_path = "./spamoverflow/spamhammer-v1.0.0-darwin-amd64"  # Update this with the actual path
    
        # Run the SpamHammer binary with any necessary arguments
        result = subprocess.run([binary_path, "scan"], input=json.dumps(json_data), capture_output=True, text=True, check=True)
        output = json.loads(result.stdout)

        #For now we simply return the output from spamhammer, later this should be handled via persistent storage etc
        return jsonify(output), 200

    except subprocess.CalledProcessError as e:
        # Handle any errors, such as if the binary fails to execute
        return jsonify({"Error trying to run spamhammer to scan an email": e})

    