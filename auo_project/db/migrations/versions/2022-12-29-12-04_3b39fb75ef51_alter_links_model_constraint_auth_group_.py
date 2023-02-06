"""alter links model constraint: auth_group_roles, auth_group_users, auth_role_actions, auth_user_actions, auth_user_roles

Revision ID: 3b39fb75ef51
Revises: b2541e553935
Create Date: 2022-12-29 12:04:47.971311

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "3b39fb75ef51"
down_revision = "b2541e553935"
branch_labels = None
depends_on = None


def upgrade() -> None:
    statments = [
        "ALTER TABLE app.auth_group_roles DROP CONSTRAINT auth_group_roles_pkey;",
        "ALTER TABLE app.auth_group_users DROP CONSTRAINT auth_group_users_pkey;",
        "ALTER TABLE app.auth_role_actions DROP CONSTRAINT auth_role_actions_pkey;",
        "ALTER TABLE app.auth_user_actions DROP CONSTRAINT auth_user_actions_pkey;",
        "ALTER TABLE app.auth_user_roles DROP CONSTRAINT auth_user_roles_pkey;",
        "ALTER TABLE app.auth_group_roles ADD PRIMARY KEY (id);",
        "ALTER TABLE app.auth_group_users ADD PRIMARY KEY (id);",
        "ALTER TABLE app.auth_role_actions ADD PRIMARY KEY (id);",
        "ALTER TABLE app.auth_user_actions ADD PRIMARY KEY (id);",
        "ALTER TABLE app.auth_user_roles ADD PRIMARY KEY (id);",
        "ALTER TABLE app.auth_group_roles ADD CONSTRAINT auth_group_roles_group_id_role_id_key UNIQUE (group_id, role_id);",
        "ALTER TABLE app.auth_group_users ADD CONSTRAINT auth_group_users_group_id_user_id_key UNIQUE (group_id, user_id);",
        "ALTER TABLE app.auth_role_actions ADD CONSTRAINT auth_role_actions_role_id_action_id_key UNIQUE (role_id, action_id);",
        "ALTER TABLE app.auth_user_actions ADD CONSTRAINT auth_user_actions_user_id_action_id_key UNIQUE (user_id, action_id);",
        "ALTER TABLE app.auth_user_roles ADD CONSTRAINT auth_user_roles_user_id_role_id_key UNIQUE (user_id, role_id);",
    ]
    conn = op.get_bind()
    for statment in statments:
        conn.execute(sa.sql.text(statment))


def downgrade() -> None:
    statments = [
        "ALTER TABLE app.auth_group_roles DROP CONSTRAINT auth_group_roles_group_id_role_id_key;",
        "ALTER TABLE app.auth_group_users DROP CONSTRAINT auth_group_users_group_id_user_id_key;",
        "ALTER TABLE app.auth_role_actions DROP CONSTRAINT auth_role_actions_role_id_action_id_key;",
        "ALTER TABLE app.auth_user_actions DROP CONSTRAINT auth_user_actions_user_id_action_id_key;",
        "ALTER TABLE app.auth_user_roles DROP CONSTRAINT auth_user_roles_user_id_role_id_key;",
        "ALTER TABLE app.auth_group_roles ADD PRIMARY KEY (id, group_id, role_id);",
        "ALTER TABLE app.auth_group_users ADD PRIMARY KEY (id, group_id, user_id);",
        "ALTER TABLE app.auth_role_actions ADD PRIMARY KEY (id, role_id, action_id);",
        "ALTER TABLE app.auth_user_actions ADD PRIMARY KEY (id, user_id, action_id);",
        "ALTER TABLE app.auth_user_roles ADD PRIMARY KEY (id, user_id, role_id);",
    ]
    conn = op.get_bind()
    for statment in statments:
        conn.execute(sa.sql.text(statment))
