from typing import List
from monitoring.domain.entities import TelemetryReading
from monitoring.infrastructure.models import TelemetryReadingModel

class TelemetryReadingRepository:
    @staticmethod
    def _to_entity(record: TelemetryReadingModel) -> TelemetryReading:
        return TelemetryReading(
            record.device_id, record.bpm, record.distance_cm, record.collision,
            record.lat, record.lng, record.created_at,
            record.id, record.synced, record.cloud_id
        )

    @staticmethod
    def save(reading: TelemetryReading) -> TelemetryReading:
        record = TelemetryReadingModel.create(
            device_id=reading.device_id,
            bpm=reading.bpm,
            distance_cm=reading.distance_cm,
            collision=reading.collision,
            lat=reading.lat,
            lng=reading.lng,
            created_at=reading.created_at,
            synced=reading.synced,
            cloud_id=reading.cloud_id,
        )
        return TelemetryReadingRepository._to_entity(record)

    @staticmethod
    def find_pending() -> List[TelemetryReading]:
        query = TelemetryReadingModel.select().where(TelemetryReadingModel.synced == False)
        return [TelemetryReadingRepository._to_entity(r) for r in query]

    @staticmethod
    def mark_synced(reading_id: int, cloud_id: int | None) -> None:
        (TelemetryReadingModel
         .update(synced=True, cloud_id=cloud_id)
         .where(TelemetryReadingModel.id == reading_id)
         .execute())