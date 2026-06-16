"""Domain entities for the IAM bounded context.

Defines the aggregate root for device identity in the edge service. Mirrors the
``Device`` aggregate of the MineGuard platform's IAM context.
"""
from datetime import datetime


class Device:
    """Aggregate root representing a registered smart-band device.

    A ``Device`` is the core identity object in the IAM bounded context. It is
    identified by a unique ``device_id`` and authenticated via its paired
    ``api_key`` (sent in the ``X-API-Key`` header). The same credentials are
    forwarded to the MineGuard cloud when telemetry is synchronized.

    Attributes:
        device_id (str): Immutable, unique identifier (e.g. ``'smart-band-001'``).
        api_key (str): Secret key used to authenticate device requests.
        created_at (datetime): UTC timestamp of device registration.
    """

    def __init__(self, device_id: str, api_key: str, created_at: datetime):
        self.device_id = device_id
        self.api_key = api_key
        self.created_at = created_at
