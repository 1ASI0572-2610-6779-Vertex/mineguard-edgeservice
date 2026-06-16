"""Flask application entry point for the MineGuard Smart Band Edge Service.

Wires the Flask application, registers the IAM and Monitoring bounded-context
Blueprints, and ensures the SQLite database is initialized (tables created, test
device seeded) once before the first HTTP request.

The Monitoring context ingests heart-rate telemetry from smart bands and
synchronizes it with the MineGuard cloud platform; the IAM context authenticates
device requests via ``device_id`` + ``X-API-Key``.

Typical usage::

    python app.py
"""
import logging

from flask import Flask

import iam.application.services
from iam.interfaces.services import iam_api
from monitoring.interfaces.services import monitoring_api
from shared.infrastructure.config import Config
from shared.infrastructure.database import init_db

logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
app.register_blueprint(iam_api)
app.register_blueprint(monitoring_api)

first_request = True


@app.before_request
def setup():
    """Initialize the database and seed the test device on the first request.

    Side effects:
        - Creates ``smart_band_edge.db`` if absent.
        - Creates the ``devices`` and ``heart_rate_readings`` tables if absent.
        - Inserts the default test device when missing.
    """
    global first_request
    if first_request:
        first_request = False
        init_db()
        auth_application_service = iam.application.services.AuthApplicationService()
        auth_application_service.get_or_create_test_device()
        app.logger.info(
            "Edge ready. Cloud sync %s -> %s",
            "ENABLED" if Config.SYNC_ENABLED else "DISABLED",
            Config.cloud_health_url(),
        )


@app.route("/health", methods=["GET"])
def health():
    """Lightweight readiness probe for the edge service itself."""
    return {"status": "ok", "cloud": Config.cloud_health_url(), "syncEnabled": Config.SYNC_ENABLED}, 200


if __name__ == "__main__":
    app.run(debug=True, port=5001)
