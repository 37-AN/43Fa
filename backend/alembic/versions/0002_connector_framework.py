"""add connector framework tables"""

from alembic import op
import sqlalchemy as sa

revision = "0002_connector_framework"
down_revision = "0001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "connectors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("schedule_cron", sa.String(length=120), nullable=True),
        sa.Column("config_json", sa.JSON(), nullable=False),
        sa.Column("created_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
    )
    op.create_index("ix_connectors_name", "connectors", ["name"], unique=True)
    op.create_index("ix_connectors_type", "connectors", ["type"], unique=False)

    op.create_table(
        "connector_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("connector_id", sa.Integer(), sa.ForeignKey("connectors.id"), nullable=False),
        sa.Column("started_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("finished_at", sa.DateTime(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("run_mode", sa.String(length=30), nullable=False, server_default="normal"),
        sa.Column("rows_fetched", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_ingested", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rows_quarantined", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("triggered_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.create_index("ix_connector_runs_connector_id", "connector_runs", ["connector_id"], unique=False)
    op.create_index("ix_connector_runs_started_at", "connector_runs", ["started_at"], unique=False)
    op.create_index("ix_connector_runs_status", "connector_runs", ["status"], unique=False)

    op.create_table(
        "connector_state",
        sa.Column("connector_id", sa.Integer(), sa.ForeignKey("connectors.id"), primary_key=True),
        sa.Column("cursor_state_json", sa.JSON(), nullable=False),
        sa.Column("last_success_ts", sa.DateTime(), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("consecutive_failures", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_table("connector_state")
    op.drop_index("ix_connector_runs_status", table_name="connector_runs")
    op.drop_index("ix_connector_runs_started_at", table_name="connector_runs")
    op.drop_index("ix_connector_runs_connector_id", table_name="connector_runs")
    op.drop_table("connector_runs")
    op.drop_index("ix_connectors_type", table_name="connectors")
    op.drop_index("ix_connectors_name", table_name="connectors")
    op.drop_table("connectors")
