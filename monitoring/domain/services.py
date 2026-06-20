"""Domain services for the Monitoring bounded context.

``HeartRateReadingService`` validates raw sensor input and constructs a
well-formed :class:`~monitoring.domain.entities.HeartRateReading`, enforcing the
bounded context invariants (plausible BPM range, valid ISO-8601 timestamp).
"""
from datetime import datetime, timezone
from dateutil.parser import parse
from monitoring.domain.entities import TelemetryReading


class TelemetryReadingService:
    """Domain service enforcing business rules on raw sensor data."""

    @staticmethod
    def create_reading(device_id: str, bpm: float, distance_cm: float, collision: bool,
                       lat: float | None, lng: float | None, created_at: str | None) -> TelemetryReading:
        try:
            bpm = float(bpm)
            distance_cm = float(distance_cm)
            collision = bool(collision)
            lat = float(lat) if lat is not None else None
            lng = float(lng) if lng is not None else None

            if not (0 <= bpm <= 250):
                raise ValueError("Invalid BPM value (must be 0-250)")
            if distance_cm < 0:
                raise ValueError("Invalid distance value (must be >= 0)")

            if created_at:
                parsed_created_at = parse(created_at).astimezone(timezone.utc)
            else:
                parsed_created_at = datetime.now(timezone.utc)

        except (ValueError, TypeError):
            raise ValueError("Invalid telemetry data format")

        return TelemetryReading(device_id, bpm, distance_cm, collision, lat, lng, parsed_created_at)
