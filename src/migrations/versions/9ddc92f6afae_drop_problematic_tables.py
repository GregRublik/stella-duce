"""drop problematic tables

Revision ID: 9ddc92f6afae
Revises: d619307681f1
Create Date: 2026-01-22 12:06:59.193621

"""
from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '9ddc92f6afae'
down_revision: Union[str, Sequence[str], None] = 'd619307681f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None



def upgrade():
    # Удаляем таблицы в правильном порядке (сначала зависимые)
    op.drop_table('user_stage_progress')
    op.drop_table('stage_dependencies')
    op.drop_table('goal_stages')
    op.drop_table('goals')
    # Добавьте другие таблицы, которые нужно удалить


def downgrade():
    # Здесь нужно будет воссоздать таблицы с их оригинальной структурой
    # Это сложно, поэтому если не критично - можно оставить пустым
    pass