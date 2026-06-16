"""Shared database infrastructure for the MineGuard Smart Band Edge Service.

Provides a single :class:`peewee.SqliteDatabase` instance (``db``) imported by
ORM models across all bounded contexts, ensuring every model operates on the
same physical database file.

The :func:`init_db` helper is called once at application start-up to open a
connection and create any missing tables without affecting existing data
(``safe=True``).
"""
from peewee import SqliteDatabase

# Shared SQLite database instance used by all bounded-context ORM models.
db = SqliteDatabase('smart_band_edge.db')


def init_db() -> None:
    """Open the database connection and create all required tables.

    Imports the ORM models from the IAM and Health bounded contexts at call
    time (deferred import) to avoid circular dependencies during module
    loading, then issues a ``CREATE TABLE IF NOT EXISTS`` for each model.

    This function is idempotent: calling it when the tables already exist is
    safe and has no side effects (``safe=True``).

    Side effects:
        - Opens a connection to ``smart_band_edge.db`` (creating the file if
          it does not exist).
        - Creates the ``devices`` table if absent.
        - Creates the ``heart_rate_readings`` table if absent.
        - Closes the connection after table creation.
    """
    db.connect()
    from iam.infrastructure.models import Device
    from monitoring.infrastructure.models import HeartRateReading
    db.create_tables([Device, HeartRateReading], safe=True)
    db.close()
