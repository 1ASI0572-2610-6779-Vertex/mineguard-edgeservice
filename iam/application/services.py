"""Application services for the IAM bounded context.

Orchestrates device-authentication use-cases by coordinating the repository and
the domain authentication service.
"""
from typing import Optional

from iam.domain.entities import Device
from iam.domain.services import AuthService
from iam.infrastructure.repositories import DeviceRepository


class AuthApplicationService:
    """Application service for device authentication and test-device bootstrap."""

    def __init__(self):
        self.device_repository = DeviceRepository()
        self.auth_service = AuthService()

    def authenticate(self, device_id: str, api_key: str) -> bool:
        """Return ``True`` when ``device_id`` / ``api_key`` match a registered device."""
        device: Optional[Device] = self.device_repository.find_by_id_and_api_key(device_id, api_key)
        return self.auth_service.authenticate(device)

    def get_api_key_for(self, device_id: str) -> Optional[str]:
        """Return the stored API key for ``device_id`` (used when syncing to the cloud)."""
        device = self.device_repository.find_by_id(device_id)
        return device.api_key if device else None

    def get_or_create_test_device(self) -> Device:
        """Retrieve the default test device, creating it if absent (development only)."""
        return self.device_repository.get_or_create_test_device()
