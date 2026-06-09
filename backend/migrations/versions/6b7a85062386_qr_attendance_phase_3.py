"""qr attendance phase 3

Revision ID: 6b7a85062386
Revises: b231a19c6a0b
Create Date: 2026-06-08 12:09:50.775177

"""
from alembic import op
import sqlalchemy as sa
import hashlib


# revision identifiers, used by Alembic.
revision = '6b7a85062386'
down_revision = 'b231a19c6a0b'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('attendance_tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('token_hash', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), server_default=sa.true(), nullable=False))
        batch_op.add_column(sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column('created_by_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('revoked_at', sa.DateTime(timezone=True), nullable=True))

    connection = op.get_bind()
    legacy_tokens = connection.execute(sa.text("SELECT id, token FROM attendance_tokens WHERE token_hash IS NULL")).fetchall()
    for token_id, token in legacy_tokens:
        connection.execute(
            sa.text("UPDATE attendance_tokens SET token_hash = :token_hash WHERE id = :token_id"),
            {"token_hash": hashlib.sha256(token.encode("utf-8")).hexdigest(), "token_id": token_id},
        )

    with op.batch_alter_table('attendance_tokens', schema=None) as batch_op:
        batch_op.alter_column('token_hash', nullable=False)
        batch_op.alter_column('is_active', server_default=None)
        batch_op.drop_index('ix_attendance_tokens_token')
        batch_op.create_index(batch_op.f('ix_attendance_tokens_is_active'), ['is_active'], unique=False)
        batch_op.create_index(batch_op.f('ix_attendance_tokens_token_hash'), ['token_hash'], unique=True)
        batch_op.create_foreign_key('fk_attendance_tokens_created_by_user_id_users', 'users', ['created_by_user_id'], ['id'])
        batch_op.drop_column('token')
        batch_op.drop_column('qr_image_path')

    with op.batch_alter_table('meeting_participants', schema=None) as batch_op:
        batch_op.add_column(sa.Column('attendance_marked_by_user_id', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('attendance_comment', sa.Text(), nullable=True))
        batch_op.create_foreign_key('fk_meeting_participants_attendance_marked_by_user_id_users', 'users', ['attendance_marked_by_user_id'], ['id'])


def downgrade():
    with op.batch_alter_table('meeting_participants', schema=None) as batch_op:
        batch_op.drop_constraint('fk_meeting_participants_attendance_marked_by_user_id_users', type_='foreignkey')
        batch_op.drop_column('attendance_comment')
        batch_op.drop_column('attendance_marked_by_user_id')

    with op.batch_alter_table('attendance_tokens', schema=None) as batch_op:
        batch_op.add_column(sa.Column('qr_image_path', sa.VARCHAR(length=512), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('token', sa.VARCHAR(length=255), autoincrement=False, nullable=True))
        batch_op.drop_constraint('fk_attendance_tokens_created_by_user_id_users', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_attendance_tokens_token_hash'))
        batch_op.drop_index(batch_op.f('ix_attendance_tokens_is_active'))

    op.execute("UPDATE attendance_tokens SET token = token_hash WHERE token IS NULL")

    with op.batch_alter_table('attendance_tokens', schema=None) as batch_op:
        batch_op.alter_column('token', nullable=False)
        batch_op.create_index('ix_attendance_tokens_token', ['token'], unique=True)
        batch_op.drop_column('revoked_at')
        batch_op.drop_column('created_by_user_id')
        batch_op.drop_column('expires_at')
        batch_op.drop_column('is_active')
        batch_op.drop_column('token_hash')
