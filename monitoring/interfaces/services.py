from flask import Blueprint, request, jsonify
from iam.interfaces.services import authenticate_request
from monitoring.application.services import CloudSyncApplicationService, TelemetryApplicationService

monitoring_api = Blueprint("monitoring_api", __name__)

telemetry_service = TelemetryApplicationService()
cloud_sync_service = CloudSyncApplicationService()

@monitoring_api.route("/api/v1/telemetry", methods=["POST"])
def create_telemetry_record():
    """Ingest unified telemetry from the IoT device."""
    auth_result = authenticate_request()
    if auth_result:
        return auth_result

    data = request.json
    try:
        device_id = data["device_id"]
        # Defaults to safe limits if sensors send partial data
        bpm = data.get("bpm", 0.0)
        distance_cm = data.get("distance_cm", 999.0)
        collision = data.get("collision", False)
        lat = data.get("lat")
        lng = data.get("lng")
        created_at = data.get("created_at")

        reading = telemetry_service.create_reading(
            device_id, bpm, distance_cm, collision, lat, lng, created_at, request.headers.get("X-API-Key")
        )

        return jsonify({
            "id": reading.id,
            "device_id": reading.device_id,
            "synced": reading.synced,
            "cloud_id": reading.cloud_id
        }), 201

    except KeyError:
        return jsonify({"error": "Missing required field: device_id"}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@monitoring_api.route("/api/v1/telemetry/sync", methods=["POST"])
def sync_pending_records():
    """Force flush of locally buffered telemetry to the cloud."""
    auth_result = authenticate_request(require_device_id=False)
    if auth_result:
        return auth_result

    summary = cloud_sync_service.sync_pending()
    return jsonify(summary), 200