"""Peewee ORM model for the Monitoring bounded context.

Defines the ``heart_rate_readings`` table that persists
:class:`~monitoring.domain.entities.HeartRateReading` entities, including the
synchronization bookkeeping fields (``synced``, ``cloud_id``).
"""
from peewee import Model, AutoField, FloatField, CharField, DateTimeField, BooleanField, IntegerField
from shared.infrastructure.database import db

class TelemetryReadingModel(Model):
    """ORM mapping for the ``heart_rate_readings`` table.

    Attributes:
        id (AutoField): Local auto-incrementing primary key.
        device_id (CharField): Device that produced the reading (loose coupling).
        bpm (FloatField): Heart-rate measurement.
        created_at (DateTimeField): UTC timestamp of the reading.
        synced (BooleanField): Whether the reading was pushed to the cloud.
        cloud_id (IntegerField): Id assigned by the MineGuard platform, if synced.
    """

    id = AutoField()
    device_id = CharField()
    bpm = FloatField()
    distance_cm = FloatField()
    collision = BooleanField()
    lat = FloatField(null=True)
    lng = FloatField(null=True)
    created_at = DateTimeField()
    synced = BooleanField(default=False)
    cloud_id = IntegerField(null=True)

    class Meta:
        database = db
        table_name = 'telemetry_readings'
