"""Shared configuration for the MineGuard Smart Band Edge Service.

Centralizes the settings required to synchronize local telemetry with the
MineGuard cloud platform. Values are read from environment variables with
development-friendly defaults so the edge works out-of-the-box against a local
MineGuard backend.

Environment variables:
    MINEGUARD_API_URL          Base URL of the MineGuard platform REST API.
    MINEGUARD_HEALTH_PATH      Ingestion path on the platform.
    MINEGUARD_SYNC_ENABLED     Whether to push records to the cloud ("true"/"false").
    MINEGUARD_SYNC_TIMEOUT     HTTP timeout (seconds) for cloud requests.
    EDGE_TEST_DEVICE_ID        Seeded development device id.
    EDGE_TEST_DEVICE_API_KEY   Seeded development device API key.
"""
import os


class Config:
    """Runtime configuration resolved from environment variables."""

    # MineGuard cloud platform (the RESTful API this edge synchronizes with).
    MINEGUARD_API_URL = os.environ.get("MINEGUARD_API_URL", "http://localhost:8080")
    MINEGUARD_HEALTH_PATH = os.environ.get(
        "MINEGUARD_HEALTH_PATH", "/api/v1/health-monitoring/data-records"
    )
    SYNC_ENABLED = os.environ.get("MINEGUARD_SYNC_ENABLED", "true").lower() == "true"
    SYNC_TIMEOUT = float(os.environ.get("MINEGUARD_SYNC_TIMEOUT", "5"))

    # Development test device (mirrors the device seeded in the MineGuard backend).
    TEST_DEVICE_ID = os.environ.get("EDGE_TEST_DEVICE_ID", "smart-band-001")
    TEST_DEVICE_API_KEY = os.environ.get("EDGE_TEST_DEVICE_API_KEY", "test-api-key-123")

    @classmethod
    def cloud_health_url(cls) -> str:
        """Return the fully-qualified MineGuard health-ingestion URL."""
        return f"{cls.MINEGUARD_API_URL.rstrip('/')}{cls.MINEGUARD_HEALTH_PATH}"
