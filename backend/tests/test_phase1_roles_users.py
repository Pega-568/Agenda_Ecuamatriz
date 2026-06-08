import pytest

from app.roles.models import RoleSlug
from app.roles.service import RoleService
from app.users.service import UserService


def test_roles_seed_created(db_session):
    roles = RoleService.seed_defaults()
    slugs = {role.slug for role in roles}
    assert slugs == {RoleSlug.ADMIN, RoleSlug.SECRETARY, RoleSlug.USER}


def test_role_names_correct(db_session):
    RoleService.seed_defaults()
    assert RoleService.get_by_slug(RoleSlug.ADMIN).name == "Administrador"
    assert RoleService.get_by_slug(RoleSlug.SECRETARY).name == "Secretaria"
    assert RoleService.get_by_slug(RoleSlug.USER).name == "Usuario"


def test_create_user_unique_email_and_password_hash(db_session):
    RoleService.seed_defaults()
    role = RoleService.get_by_slug(RoleSlug.USER)
    user = UserService.create_user(
        {
            "full_name": "Persona Prueba",
            "email": "persona@test.local",
            "password": "Secret123!",
            "role_id": role.id,
        }
    )
    assert user.id is not None
    assert user.password_hash != "Secret123!"
    assert UserService.check_password(user, "Secret123!")

    with pytest.raises(ValueError):
        UserService.create_user(
            {
                "full_name": "Persona Prueba",
                "email": "persona@test.local",
                "password": "Secret123!",
                "role_id": role.id,
            }
        )


def test_user_activate_deactivate(db_session, regular_user):
    UserService.set_active(regular_user.id, False)
    assert UserService.get_by_id(regular_user.id).is_active is False
    UserService.set_active(regular_user.id, True)
    assert UserService.get_by_id(regular_user.id).is_active is True


def test_search_user_by_name_or_email(db_session, regular_user):
    by_name = UserService.search("Usuario")
    by_email = UserService.search(regular_user.email)
    assert regular_user.id in {user.id for user in by_name}
    assert regular_user.id in {user.id for user in by_email}
