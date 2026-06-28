"""
Alembic environment configuration.
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
from pathlib import Path

# Add parent directory to path to import app models
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.base import Base
from app.models import Drone, Zone, Event, Operator  # noqa: F401

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def include_object(object, name, type_, reflected, compare_to):
    """
    Filter objects to include in migrations.
    Exclude PostGIS system tables and extensions.
    """
    if type_ == "table":
        # Exclude PostGIS tiger_geocoder and other system tables
        if name in [
            "state", "state_lookup", "place", "place_lookup",
            "county", "county_lookup", "cousub", "cousub_lookup",
            "edges", "faces", "zcta5", "zip_lookup", "zip_lookup_all",
            "zip_state", "zip_state_loc", "addrfeat", "addr",
            "bg", "tract", "tabblock20", "tabblock", "pagc_gaz",
            "pagc_lex", "pagc_rules", "geocode_settings",
            "geocode_settings_default", "loader_platform",
            "loader_lookuptables", "spatial_ref_sys", "topology",
            "layer", "direction_lookup", "secondary_unit_lookup",
            "street_type_lookup"
        ]:
            return False
        # Exclude tables starting with tiger_
        if name.startswith("tiger_"):
            return False
    return True


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
