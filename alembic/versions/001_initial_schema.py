"""Initial schema migration for SmartInfra AI

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-08-22 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '001_initial_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('name', sa.String(length=150), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Officers table
    op.create_table(
        'officers',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, unique=True),
        sa.Column('employee_id', sa.String(length=50), nullable=False, unique=True),
        sa.Column('department', sa.String(length=150), nullable=False),
        sa.Column('designation', sa.String(length=150), nullable=False),
        sa.Column('phone', sa.String(length=30), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('office', sa.String(length=255), nullable=True),
        sa.Column('public_contact', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Infrastructure Assets table
    op.create_table(
        'infrastructure_assets',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('asset_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geometry_wkt', sa.Text(), nullable=True),
        sa.Column('installation_date', sa.Date(), nullable=True),
        sa.Column('material', sa.String(length=100), nullable=True),
        sa.Column('age', sa.Float(), nullable=False, default=0.0),
        sa.Column('criticality', sa.String(length=50), nullable=False, default='MEDIUM'),
        sa.Column('condition', sa.String(length=100), nullable=False, default='Good'),
        sa.Column('health_score', sa.Float(), nullable=False, default=100.0),
        sa.Column('risk_score', sa.Float(), nullable=False, default=0.0),
        sa.Column('status', sa.String(length=50), nullable=False, default='NORMAL'),
        sa.Column('source', sa.String(length=150), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('source_record_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Government Projects table
    op.create_table(
        'government_projects',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('project_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('department', sa.String(length=150), nullable=False),
        sa.Column('project_type', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='ONGOING'),
        sa.Column('progress', sa.Float(), nullable=False, default=0.0),
        sa.Column('start_date', sa.Date(), nullable=True),
        sa.Column('expected_end_date', sa.Date(), nullable=True),
        sa.Column('actual_end_date', sa.Date(), nullable=True),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('geometry_wkt', sa.Text(), nullable=True),
        sa.Column('officer_id', sa.Integer(), sa.ForeignKey('officers.id', ondelete='SET NULL'), nullable=True),
        sa.Column('source', sa.String(length=150), nullable=True),
        sa.Column('source_url', sa.String(length=500), nullable=True),
        sa.Column('last_updated', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Sensors table
    op.create_table(
        'sensors',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('sensor_id', sa.String(length=100), nullable=False, unique=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('infrastructure_assets.id', ondelete='CASCADE'), nullable=True),
        sa.Column('sensor_type', sa.String(length=50), nullable=False),
        sa.Column('device_type', sa.String(length=50), nullable=False, default='OTHER'),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='ONLINE'),
        sa.Column('installed_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen', sa.DateTime(), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=True),
        sa.Column('longitude', sa.Float(), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
    )

    # Sensor Readings table
    op.create_table(
        'sensor_readings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('sensor_id', sa.String(length=100), sa.ForeignKey('sensors.sensor_id', ondelete='CASCADE'), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.Column('value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(length=50), nullable=False),
        sa.Column('quality', sa.String(length=50), nullable=False, default='GOOD'),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
    )

    # Warnings table
    op.create_table(
        'warnings',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('infrastructure_assets.id', ondelete='CASCADE'), nullable=True),
        sa.Column('project_id', sa.Integer(), sa.ForeignKey('government_projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('warning_type', sa.String(length=100), nullable=False),
        sa.Column('severity', sa.String(length=50), nullable=False, default='MODERATE'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('risk_score', sa.Float(), nullable=False),
        sa.Column('trigger', sa.String(length=255), nullable=False),
        sa.Column('recommended_action', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, default='ACTIVE'),
        sa.Column('acknowledged_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('acknowledged_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Precautions table
    op.create_table(
        'precautions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('warning_id', sa.Integer(), sa.ForeignKey('warnings.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=50), nullable=False, default='MEDIUM'),
        sa.Column('action', sa.Text(), nullable=False),
        sa.Column('target_audience', sa.String(length=50), nullable=False, default='CITIZEN'),
    )

    # Predictions table
    op.create_table(
        'predictions',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('infrastructure_assets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('prediction_type', sa.String(length=50), nullable=False),
        sa.Column('probability', sa.Float(), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False, default=0.75),
        sa.Column('predicted_failure_window', sa.String(length=100), nullable=True),
        sa.Column('estimated_rul_min', sa.Float(), nullable=True),
        sa.Column('estimated_rul_max', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=False),
        sa.Column('features', sa.JSON(), nullable=True),
        sa.Column('explanation', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )

    # Work Orders table
    op.create_table(
        'work_orders',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('asset_id', sa.Integer(), sa.ForeignKey('infrastructure_assets.id', ondelete='CASCADE'), nullable=False),
        sa.Column('warning_id', sa.Integer(), sa.ForeignKey('warnings.id', ondelete='SET NULL'), nullable=True),
        sa.Column('assigned_to', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('priority', sa.String(length=50), nullable=False, default='MEDIUM'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, default='OPEN'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('verification_notes', sa.Text(), nullable=True),
    )

    # Audit Logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=100), nullable=False),
        sa.Column('entity_id', sa.String(length=100), nullable=True),
        sa.Column('metadata_json', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('work_orders')
    op.drop_table('predictions')
    op.drop_table('precautions')
    op.drop_table('warnings')
    op.drop_table('sensor_readings')
    op.drop_table('sensors')
    op.drop_table('government_projects')
    op.drop_table('infrastructure_assets')
    op.drop_table('officers')
    op.drop_table('users')
