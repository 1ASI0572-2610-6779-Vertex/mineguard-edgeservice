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
    @staticmethod
    def find_by_id_and_api_key(device_id: str, api_key: str) -> Optional[Device]:
        try:
            device = DeviceModel.get((DeviceModel.device_id == device_id) & (DeviceModel.api_key == api_key))
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def find_by_id(device_id: str) -> Optional[Device]:
        try:
            device = DeviceModel.get(DeviceModel.device_id == device_id)
            return Device(device.device_id, device.api_key, device.created_at)
        except peewee.DoesNotExist:
            return None

    @staticmethod
    def get_or_create_test_device() -> Device:
        device, _ = DeviceModel.get_or_create(
            device_id=Config.TEST_DEVICE_ID,
            defaults={"api_key": Config.TEST_DEVICE_API_KEY, "created_at": "2025-01-01T00:00:00Z"},
        )
        return Device(device.device_id, device.api_key, device.created_at)