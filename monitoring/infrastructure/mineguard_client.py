"""Anti-corruption client for the MineGuard cloud platform.

Encapsulates the HTTP contract of the MineGuard platform's heart-rate ingestion
endpoint (``POST /api/v1/health-monitoring/data-records``). This is the outbound
adapter that realizes the "cloud synchronization" capability: it shields the
edge domain from the cloud's wire format and transport concerns.
"""
import logging
from typing import Optional

import requests

from monitoring.domain.entities import HeartRateReading
from shared.infrastructure.config import Config

logger = logging.getLogger(__name__)


class MineGuardCloudClient:
    """HTTP client that pushes heart-rate readings to the MineGuard platform."""

    @staticmethod
    def push_reading(reading: HeartRateReading, api_key: str) -> Optional[int]:
        """Push a single reading to the MineGuard cloud ingestion endpoint.

        Sends ``{device_id, bpm, created_at}`` with the device ``X-API-Key``
        header, matching the platform's contract. The platform persists the
        reading and may raise a fatigue alert on abnormal values.

        Args:
            reading (HeartRateReading): The local reading to synchronize.
            api_key (str): The device's API key (forwarded as ``X-API-Key``).

        Returns:
            Optional[int]: The cloud-assigned record id on success (HTTP 201);
            ``None`` if the push failed (network error or non-success status).
        """
        url = Config.cloud_health_url()
        payload = {
            "device_id": reading.device_id,
            "bpm": reading.bpm,
            "created_at": reading.created_at.isoformat()
            if hasattr(reading.created_at, "isoformat") else str(reading.created_at),
        }
        headers = {"Content-Type": "application/json", "X-API-Key": api_key}
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=Config.SYNC_TIMEOUT)
            if response.status_code == 201:
                body = response.json()
                return body.get("id")
            logger.warning("MineGuard sync rejected (HTTP %s): %s", response.status_code, response.text)
            return None
        except requests.RequestException as exc:
            logger.warning("MineGuard sync failed (cloud unreachable): %s", exc)
            return None
