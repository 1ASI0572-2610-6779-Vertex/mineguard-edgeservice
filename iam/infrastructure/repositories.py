"""Repository implementation for the IAM bounded context.

Maps between the :class:`~iam.domain.entities.Device` domain entity and the
:class:`~iam.infrastructure.models.Device` Peewee model, keeping the domain
layer free of ORM concerns.
"""
from typing import Optional

import peewee

from iam.domain.entities import Device
from iam.infrastructure.models import Device as DeviceModel
from shared.infrastructure.config import Config


class DeviceRepository:
    """Persists and reconstructs :class:`~iam.domain.entities.Device` entities."""

    @staticmethod
    def find_by_id_and_api_key(device_id: str, api_key: str) -> Optional[Device]:
        """Return the device matching both ``device_id`` and ``api_key``, or ``None``."""
        try:
            device = DeviceModel.get(
                (DeviceModel.device_id == device_id) & (DeviceModel.api_key == api_key)
            )
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(device_id: str) -> Optional[Device]:
        """Return the device matching ``device_id`` (used to resolve its API key for sync)."""
        try:
            device = DeviceModel.get(DeviceModel.device_id == device_id)
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_test_device() -> Device:
        """Idempotently create the development test device defined in :class:`Config`."""
        device, _ = DeviceModel.get_or_create(
            device_id=Config.TEST_DEVICE_ID,
            defaults={"api_key": Config.TEST_DEVICE_API_KEY, "created_at": "2025-06-04T23:23:00Z"},
        )
        return Device(device.device_id, device.api_key, device.created_at)
