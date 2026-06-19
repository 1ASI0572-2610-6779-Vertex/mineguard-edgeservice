"""Application services for the Monitoring bounded context.

Orchestrate the *ingest heart-rate reading* and *synchronize to cloud*
use-cases by coordinating IAM (device validation), the domain service, the
repository and the MineGuard cloud client.
"""
import logging

from iam.infrastructure.repositories import DeviceRepository
from monitoring.domain.entities import HeartRateReading
from monitoring.domain.services import HeartRateReadingService
from monitoring.infrastructure.mineguard_client import MineGuardCloudClient
from monitoring.infrastructure.repositories import HeartRateReadingRepository
from shared.infrastructure.config import Config

logger = logging.getLogger(__name__)


class HeartRateApplicationService:
    """Orchestrates the *ingest heart-rate reading* use-case.

    1. Cross-context guard: validates the device via the IAM repository.
    2. Domain logic: validates the raw values and builds the reading.
    3. Persistence: stores the reading locally (SQLite).
    4. Synchronization: best-effort push to the MineGuard cloud; on success the
       reading is marked as synced with its cloud id. Failures never break local
       ingestion — the reading remains pending and can be flushed later.
    """

    def __init__(self):
        self.heart_rate_repository = HeartRateReadingRepository()
        self.heart_rate_service = HeartRateReadingService()
        self.device_repository = DeviceRepository()

    def create_reading(self, device_id: str, bpm: float, created_at: str, api_key: str) -> HeartRateReading:
        """Validate, persist and (best-effort) synchronize a heart-rate reading.

        Raises:
            ValueError: If the device/API-key pair is unknown or the sensor
                values are invalid.
        """
        if not self.device_repository.find_by_id_and_api_key(device_id, api_key):
            raise ValueError("Device not found")
        reading = self.heart_rate_service.create_reading(device_id, bpm, created_at)
        saved = self.heart_rate_repository.save(reading)

        if Config.SYNC_ENABLED:
            cloud_id = MineGuardCloudClient.push_reading(saved, api_key)
            if cloud_id is not None:
                self.heart_rate_repository.mark_synced(saved.id, cloud_id)
                saved.synced = True
                saved.cloud_id = cloud_id
        return saved


class CloudSyncApplicationService:
    """Orchestrates the *synchronize pending readings to cloud* use-case.

    Flushes every locally-stored reading that has not yet reached the MineGuard
    platform, resolving each device's API key from the IAM repository.
    """

    def __init__(self):
        self.heart_rate_repository = HeartRateReadingRepository()
        self.device_repository = DeviceRepository()

    def sync_pending(self) -> dict:
        """Push all pending readings to the cloud.

        Returns:
            dict: A summary ``{"pending", "synced", "failed"}`` of the batch.
        """
        pending = self.heart_rate_repository.find_pending()
        synced = 0
        failed = 0
        for reading in pending:
            device = self.device_repository.find_by_id(reading.device_id)
            if device is None:
                failed += 1
                continue
            cloud_id = MineGuardCloudClient.push_reading(reading, device.api_key)
            if cloud_id is not None:
                self.heart_rate_repository.mark_synced(reading.id, cloud_id)
                synced += 1
            else:
                failed += 1
        logger.info("Cloud sync finished: %s synced, %s failed of %s pending", synced, failed, len(pending))
        return {"pending": len(pending), "synced": synced, "failed": failed}
