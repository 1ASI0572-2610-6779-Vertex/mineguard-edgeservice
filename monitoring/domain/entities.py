"""Domain entities for the Monitoring bounded context.

Heart-rate telemetry captured by a smart band belongs to Monitoring (the same
context that owns sensor readings and alerts in the MineGuard platform).
"""
from datetime import datetime
from typing import Optional


class HeartRateReading:
    """Aggregate root representing a single heart-rate reading.

    Captures a beats-per-minute measurement taken by a smart-band device at a
    point in time. Created by
    :meth:`~monitoring.domain.services.HeartRateReadingService.create_reading`
    after validation, then persisted and (best-effort) synchronized to the
    MineGuard cloud platform.

    Attributes:
        id (int | None): Local surrogate id; ``None`` for transient instances.
        device_id (str): Identifier of the device that produced the reading.
        bpm (float): Heart-rate in beats per minute.
        created_at (datetime): UTC timestamp of the reading.
        synced (bool): Whether this reading has been pushed to the cloud.
        cloud_id (int | None): Id assigned by the MineGuard platform on sync.
    """

    def __init__(self, device_id: str, bpm: float, created_at: datetime,
                 id: int = None, synced: bool = False, cloud_id: Optional[int] = None):
        self.id = id
        self.device_id = device_id
        self.bpm = bpm
        self.created_at = created_at
        self.synced = synced
        self.cloud_id = cloud_id
