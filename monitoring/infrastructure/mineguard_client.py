import logging
import requests
from typing import Optional
from monitoring.domain.entities import TelemetryReading
from shared.infrastructure.config import Config

logger = logging.getLogger(__name__)

class MineGuardCloudClient:
    """Anti-corruption layer for the unified MineGuard cloud platform."""

    @staticmethod
    def push_reading(reading: TelemetryReading, api_key: str) -> bool:
        url = Config.cloud_telemetry_url()

        payload = {
            "device_id": reading.device_id,
            "bpm": reading.bpm,
            "distance_cm": reading.distance_cm,
            "collision": reading.collision,
            "lat": reading.lat,
            "lng": reading.lng,
            "timestamp": reading.created_at.isoformat() if hasattr(reading.created_at, "isoformat") else str(reading.created_at)
        }

        headers = {
            "Content-Type": "application/json",
            "X-API-Key": api_key
        }

        try:
            response = requests.post(url, json=payload, headers=headers, timeout=Config.SYNC_TIMEOUT)
            if response.status_code == 201:
                cloud_data = response.json()
                logger.info(f"Cloud sync OK. Processed: {cloud_data.get('processed')}")
                return True

            logger.warning("Cloud rejected telemetry (HTTP %s): %s", response.status_code, response.text)
            return False
        except requests.RequestException as exc:
            logger.warning("Cloud unreachable (Store & Forward triggered): %s", exc)
            return False