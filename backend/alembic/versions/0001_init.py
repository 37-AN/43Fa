"""init tables"""

from alembic import op
import sqlalchemy as sa

revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("users", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("username", sa.String(50), nullable=False), sa.Column("hashed_password", sa.String(255), nullable=False), sa.Column("role", sa.String(20), nullable=False))
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    op.create_table("datasets", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("name", sa.String(120), nullable=False), sa.Column("uploaded_at", sa.DateTime(), nullable=False), sa.Column("row_count", sa.Integer(), nullable=False))

    op.create_table("machines", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("machine_code", sa.String(50), nullable=False))
    op.create_index("ix_machines_machine_code", "machines", ["machine_code"], unique=True)

    op.create_table("operators", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("operator_code", sa.String(50), nullable=False))
    op.create_index("ix_operators_operator_code", "operators", ["operator_code"], unique=True)

    op.create_table("production_records", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("dataset_id", sa.Integer(), sa.ForeignKey("datasets.id"), nullable=False), sa.Column("machine_id", sa.Integer(), sa.ForeignKey("machines.id"), nullable=False), sa.Column("operator_id", sa.Integer(), sa.ForeignKey("operators.id"), nullable=False), sa.Column("shift", sa.String(20), nullable=False), sa.Column("timestamp", sa.DateTime(), nullable=False), sa.Column("report_date", sa.Date(), nullable=False), sa.Column("downtime_minutes", sa.Float(), nullable=False), sa.Column("scrap_units", sa.Float(), nullable=False), sa.Column("output_units", sa.Float(), nullable=False))
    op.create_index("ix_production_records_report_date", "production_records", ["report_date"])

    op.create_table("daily_aggregates", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("report_date", sa.Date(), nullable=False), sa.Column("machine_code", sa.String(50), nullable=False), sa.Column("shift", sa.String(20), nullable=False), sa.Column("downtime_minutes", sa.Float(), nullable=False), sa.Column("scrap_units", sa.Float(), nullable=False), sa.Column("output_units", sa.Float(), nullable=False))

    op.create_table("anomalies", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("report_date", sa.Date(), nullable=False), sa.Column("machine_code", sa.String(50), nullable=False), sa.Column("metric", sa.String(50), nullable=False), sa.Column("value", sa.Float(), nullable=False), sa.Column("baseline", sa.Float(), nullable=False), sa.Column("z_score", sa.Float(), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("insight", sa.Text(), nullable=False))


def downgrade() -> None:
    op.drop_table("anomalies")
    op.drop_table("daily_aggregates")
    op.drop_table("production_records")
    op.drop_table("operators")
    op.drop_table("machines")
    op.drop_table("datasets")
    op.drop_index("ix_users_username", table_name="users")
    op.drop_table("users")
