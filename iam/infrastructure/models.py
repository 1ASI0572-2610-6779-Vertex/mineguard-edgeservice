"""Peewee ORM model for the IAM bounded context.

Defines the ``devices`` table used to persist :class:`~iam.domain.entities.Device`
aggregate roots. Belongs to the infrastructure layer; access is mediated through
the repository.
"""
from peewee import Model, CharField, DateTimeField

from shared.infrastructure.database import db


class Device(Model):
    """ORM mapping for the ``devices`` table.

    Attributes:
        device_id (CharField): Natural primary key (e.g. ``'smart-band-001'``).
        api_key (CharField): Secret key checked on every authenticated call.
        created_at (DateTimeField): UTC registration timestamp.
    """

    device_id = CharField(primary_key=True)
    api_key = CharField()
    created_at = DateTimeField()

    class Meta:
        database = db
        table_name = 'devices'
