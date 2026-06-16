"""Domain services for the IAM bounded context.

``AuthService`` encapsulates the device-authentication invariant: a device is
authenticated when it exists in the repository (matched by ``device_id`` and
``api_key``).
"""
from typing import Optional

from iam.domain.entities import Device


class AuthService:
    """Domain service that decides whether a device is authenticated."""

    @staticmethod
    def authenticate(device: Optional[Device]) -> bool:
        """Return ``True`` when the device look-up succeeded (non-``None``)."""
        return device is not None
