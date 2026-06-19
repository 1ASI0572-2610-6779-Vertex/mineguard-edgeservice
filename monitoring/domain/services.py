"""Domain services for the Monitoring bounded context.

``HeartRateReadingService`` validates raw sensor input and constructs a
well-formed :class:`~monitoring.domain.entities.HeartRateReading`, enforcing the
bounded context invariants (plausible BPM range, valid ISO-8601 timestamp).
"""
from datetime import datetime, timezone

from dateutil.parser import parse

from monitoring.domain.entities import HeartRateReading


class HeartRateReadingService:
    """Domain service responsible for creating valid heart-rate readings."""

    @staticmethod
    def create_reading(device_id: str, bpm: float, created_at: str | None) -> HeartRateReading:
        """Validate raw sensor data and build a new :class:`HeartRateReading`.

        Invariants:
            * ``bpm`` is coerced to ``float`` and must fall within [0, 200].
            * ``created_at`` is parsed and normalized to UTC; when ``None`` the
              current UTC time is used.

        Raises:
            ValueError: If ``bpm`` is not numeric, is out of range, or
                ``created_at`` is not a valid ISO-8601 string.
        """
        try:
            bpm = float(bpm)
            if not (0 <= bpm <= 200):
                raise ValueError("Invalid BPM value")
            if created_at:
                parsed_created_at = parse(created_at).astimezone(timezone.utc)
            else:
                parsed_created_at = datetime.now(timezone.utc)
        except (ValueError, TypeError):
            raise ValueError("Invalid data format")

        return HeartRateReading(device_id, bpm, parsed_created_at)
