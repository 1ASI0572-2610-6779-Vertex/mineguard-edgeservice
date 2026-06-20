import logging
from iam.infrastructure.repositories import DeviceRepository
from monitoring.domain.entities import TelemetryReading
from monitoring.domain.services import TelemetryReadingService
from monitoring.infrastructure.mineguard_client import MineGuardCloudClient
from monitoring.infrastructure.repositories import TelemetryReadingRepository
from shared.infrastructure.config import Config

logger = logging.getLogger(__name__)

class TelemetryApplicationService:
    def __init__(self):
        self.telemetry_repo = TelemetryReadingRepository()
        self.telemetry_service = TelemetryReadingService()
        self.device_repo = DeviceRepository()

    def create_reading(self, device_id: str, bpm: float, distance_cm: float, collision: bool,
                       lat: float, lng: float, created_at: str, api_key: str) -> TelemetryReading:

        if not self.device_repo.find_by_id_and_api_key(device_id, api_key):
            raise ValueError("Device authentication failed in application layer")

        reading = self.telemetry_service.create_reading(device_id, bpm, distance_cm, collision, lat, lng, created_at)
        saved = self.telemetry_repo.save(reading)

        if Config.SYNC_ENABLED:
            sync_success = MineGuardCloudClient.push_reading(saved, api_key)
            if sync_success:
                self.telemetry_repo.mark_synced(saved.id, cloud_id=None)
                saved.synced = True

        return saved


class CloudSyncApplicationService:
    def __init__(self):
        self.telemetry_repo = TelemetryReadingRepository()
        self.device_repo = DeviceRepository()

    def sync_pending(self) -> dict:
        pending = self.telemetry_repo.find_pending()
        synced, failed = 0, 0

        for reading in pending:
            device = self.device_repo.find_by_id(reading.device_id)
            if not device:
                failed += 1
                continue

            sync_success = MineGuardCloudClient.push_reading(reading, device.api_key)
            if sync_success:
                self.telemetry_repo.mark_synced(reading.id, cloud_id=None)
                synced += 1
            else:
                failed += 1

        logger.info(f"Sync complete: {synced} synced, {failed} failed out of {len(pending)} pending.")
        return {"pending": len(pending), "synced": synced, "failed": failed}