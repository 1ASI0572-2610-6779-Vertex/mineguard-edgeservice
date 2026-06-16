"""Interface (REST) layer for the IAM bounded context.

Exposes a Flask Blueprint (``iam_api``) and a shared ``authenticate_request``
helper used by other bounded contexts to guard their endpoints. Owns no domain
logic; concerned only with HTTP request/response handling.
"""
from flask import Blueprint, request, jsonify

from iam.application.services import AuthApplicationService

iam_api = Blueprint("iam_api", __name__)

# Module-level singleton — instantiated once per worker process.
auth_service = AuthApplicationService()


def authenticate_request():
    """Validate the device identity for an incoming HTTP request.

    Extracts ``device_id`` from the JSON body and ``X-API-Key`` from the
    headers, then delegates to the IAM application service.

    Returns:
        tuple[flask.Response, int] | None: A ``(JSON, 401)`` tuple when
        authentication fails; ``None`` when the request is authenticated.
    """
    data = request.get_json(silent=True) or {}
    device_id = data.get("device_id")
    api_key = request.headers.get("X-API-Key")
    if not device_id or not api_key:
        return jsonify({"error": "Missing device_id or X-API-Key"}), 401
    if not auth_service.authenticate(device_id, api_key):
        return jsonify({"error": "Invalid device_id or API key"}), 401
    return None
