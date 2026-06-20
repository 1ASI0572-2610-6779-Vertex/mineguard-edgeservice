from flask import Blueprint, request, jsonify
from iam.application.services import AuthApplicationService

iam_api = Blueprint("iam_api", __name__)

# Module-level singleton
auth_service = AuthApplicationService()

def authenticate_request(require_device_id=True):
    """Validate the device identity for an incoming HTTP request."""
    api_key = request.headers.get("X-API-Key")

    if not api_key:
        return jsonify({"error": "Unauthorized: Missing X-API-Key in headers"}), 401

    if require_device_id:
        data = request.get_json(silent=True) or {}
        device_id = data.get("device_id")

        if not device_id:
            return jsonify({"error": "Missing device_id in body"}), 400

        if not auth_service.authenticate(device_id, api_key):
            return jsonify({"error": "Unauthorized: Invalid device credentials"}), 401
    else:

        from shared.infrastructure.config import Config
        if api_key != Config.TEST_DEVICE_API_KEY:
            return jsonify({"error": "Unauthorized: Invalid API Key"}), 401

    return None