"""Interface (REST) layer for the Monitoring bounded context.

Exposes a Flask Blueprint (``monitoring_api``) with the heart-rate ingestion
endpoint (mirroring the MineGuard platform contract) and a manual cloud-sync
endpoint to flush readings that were buffered while the cloud was unreachable.
"""
from flask import Blueprint, request, jsonify

from iam.interfaces.services import authenticate_request
from monitoring.application.services import CloudSyncApplicationService, HeartRateApplicationService

monitoring_api = Blueprint("monitoring_api", __name__)

heart_rate_service = HeartRateApplicationService()
cloud_sync_service = CloudSyncApplicationService()


@monitoring_api.route("/api/v1/health-monitoring/data-records", methods=["POST"])
def create_health_record():
    """Create a new heart-rate record for an authenticated smart-band device.

    Headers:
        X-API-Key (required): the device's API key.
        Content-Type: application/json.

    Body (JSON):
        device_id (str, required), bpm (float, required),
        created_at (str, optional ISO-8601; defaults to current UTC).

    Responses:
        201 Created — record persisted locally (and pushed to the cloud when
            reachable). Body includes ``id, device_id, bpm, created_at, synced,
            cloud_id``.
        400 Bad Request — missing required fields or invalid values.
        401 Unauthorized — missing/invalid device credentials.
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        device_id = data["device_id"]
        bpm = data["bpm"]
        created_at = data.get("created_at")
        reading = heart_rate_service.create_reading(
            device_id, bpm, created_at, request.headers.get("X-API-Key")
        )
        return jsonify({
            "id": reading.id,
            "device_id": reading.device_id,
            "bpm": reading.bpm,
            "created_at": reading.created_at.isoformat() + "Z"
            if hasattr(reading.created_at, "isoformat") else str(reading.created_at),
            "synced": reading.synced,
            "cloud_id": reading.cloud_id,
        }), 201
    except KeyError:
        return jsonify({"error": "Missing required fields"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@monitoring_api.route("/api/v1/health-monitoring/sync", methods=["POST"])
def sync_pending_records():
    """Flush all locally-buffered readings to the MineGuard cloud platform.

    Useful after the edge has been offline: any reading with ``synced = false``
    is retried against the cloud ingestion endpoint.

    Headers:
        X-API-Key (required): a valid device API key to authorize the operation.

    Responses:
        200 OK — summary ``{pending, synced, failed}``.
        401 Unauthorized — missing/invalid device credentials.
    """
    auth_result = authenticate_request()
    if auth_result:
        return auth_result
    summary = cloud_sync_service.sync_pending()
    return jsonify(summary), 200
