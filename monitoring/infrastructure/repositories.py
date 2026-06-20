"""Repository implementation for the Monitoring bounded context.

Maps between the :class:`~monitoring.domain.entities.HeartRateReading` domain
entity and its Peewee model, and exposes the queries needed for cloud
synchronization (pending readings, mark-as-synced).
"""
from typing import List

from monitoring.domain.entities import HeartRateReading
from monitoring.infrastructure.models import HeartRateReading as HeartRateReadingModel


class HeartRateReadingRepository:
    """Persists and reconstructs heart-rate readings backed by SQLite."""

    @staticmethod
    def _to_entity(record: HeartRateReadingModel) -> HeartRateReading:
        return HeartRateReading(
            record.device_id, record.bpm, record.created_at,
            record.id, record.synced, record.cloud_id,
        )

    @staticmethod
    def save(reading: HeartRateReading) -> HeartRateReading:
        """Insert a new reading and return it enriched with the assigned ``id``."""
        record = HeartRateReadingModel.create(
            device_id=reading.device_id,
            bpm=reading.bpm,
            created_at=reading.created_at,
            synced=reading.synced,
            cloud_id=reading.cloud_id,
        )
        return HeartRateReadingRepository._to_entity(record)

    @staticmethod
    def find_pending() -> List[HeartRateReading]:
        """Return all readings that have not yet been synced to the cloud."""
        query = HeartRateReadingModel.select().where(HeartRateReadingModel.synced == False)
        return [HeartRateReadingRepository._to_entity(r) for r in query]

    @staticmethod
    def mark_synced(reading_id: int, cloud_id: int | None) -> None:
        """Mark a local reading as synchronized, storing the cloud-assigned id."""
        (HeartRateReadingModel
         .update(synced=True, cloud_id=cloud_id)
         .where(HeartRateReadingModel.id == reading_id)
         .execute())
