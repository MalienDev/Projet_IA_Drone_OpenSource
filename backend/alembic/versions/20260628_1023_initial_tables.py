"""Initial migration

Revision ID: initial
Revises: 
Create Date: 2026-06-28 10:23:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create drones table
    op.create_table(
        'drones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('stream_url', sa.String(), nullable=False),
        sa.Column('link_type', sa.String(), nullable=False),
        sa.Column('status', sa.String(), server_default='offline'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_drones_id'), 'drones', ['id'], unique=False)

    # Create operators table
    op.create_table(
        'operators',
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.String(), server_default='operator'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('username')
    )
    op.create_index(op.f('ix_operators_username'), 'operators', ['username'], unique=False)

    # Create zones table
    op.create_table(
        'zones',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('polygon_geojson', postgresql.JSON(), nullable=False),
        sa.Column('zone_type', sa.String(), nullable=False),
        sa.Column('rules_json', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_zones_id'), 'zones', ['id'], unique=False)

    # Create events table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('alert_id', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('drone_id', sa.String(), nullable=False),
        sa.Column('event_type', sa.String(), nullable=False),
        sa.Column('severity', sa.String(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('bbox', postgresql.JSON(), nullable=False),
        sa.Column('track_id', sa.String(), nullable=True),
        sa.Column('zone_id', sa.String(), nullable=True),
        sa.Column('geo', postgresql.JSON(), nullable=True),
        sa.Column('snapshot_path', sa.String(), nullable=True),
        sa.Column('clip_path', sa.String(), nullable=True),
        sa.Column('requires_operator_ack', sa.Boolean(), server_default='true'),
        sa.Column('acknowledged_by', sa.String(), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['acknowledged_by'], ['operators.username'], ),
        sa.ForeignKeyConstraint(['drone_id'], ['drones.id'], ),
        sa.ForeignKeyConstraint(['zone_id'], ['zones.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('alert_id')
    )
    op.create_index(op.f('ix_events_alert_id'), 'events', ['alert_id'], unique=False)
    op.create_index(op.f('ix_events_drone_id'), 'events', ['drone_id'], unique=False)
    op.create_index(op.f('ix_events_event_type'), 'events', ['event_type'], unique=False)
    op.create_index(op.f('ix_events_severity'), 'events', ['severity'], unique=False)
    op.create_index(op.f('ix_events_timestamp'), 'events', ['timestamp'], unique=False)
    op.create_index(op.f('ix_events_track_id'), 'events', ['track_id'], unique=False)
    op.create_index(op.f('ix_events_zone_id'), 'events', ['zone_id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_events_zone_id'), table_name='events')
    op.drop_index(op.f('ix_events_track_id'), table_name='events')
    op.drop_index(op.f('ix_events_timestamp'), table_name='events')
    op.drop_index(op.f('ix_events_severity'), table_name='events')
    op.drop_index(op.f('ix_events_event_type'), table_name='events')
    op.drop_index(op.f('ix_events_drone_id'), table_name='events')
    op.drop_index(op.f('ix_events_alert_id'), table_name='events')
    op.drop_table('events')
    op.drop_index(op.f('ix_zones_id'), table_name='zones')
    op.drop_table('zones')
    op.drop_index(op.f('ix_operators_username'), table_name='operators')
    op.drop_table('operators')
    op.drop_index(op.f('ix_drones_id'), table_name='drones')
    op.drop_table('drones')
