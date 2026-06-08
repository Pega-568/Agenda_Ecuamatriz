"""
scripts/seed_all.py — Seeder principal
Agenda Ecuamatriz

Ejecutar desde la carpeta backend/:
    python scripts/seed_all.py

Inserta datos iniciales necesarios para arrancar el sistema:
    1. Roles del sistema (admin, secretaria, usuario)
    2. Usuarios demo: admin, secretaría, usuario colaborador
    3. Áreas organizacionales base
    4. Salas de reunión base
    5. Configuración del sistema por defecto
    6. Horario laboral por defecto (lunes-viernes, 08:00-17:00)

IMPORTANTE:
    - IDEMPOTENTE: puede ejecutarse múltiples veces sin duplicar datos.
    - No guardar contraseñas en texto plano; se hashean con bcrypt.
    - No usar contraseñas demo en producción; cambiarlas inmediatamente.
    - Requiere PostgreSQL Docker corriendo (docker compose up -d).

Decisión (Cierre Fase 0):
    Driver BD: psycopg (v3) — DATABASE_URL debe usar postgresql+psycopg://
"""

import sys
import os

# Asegurar que el path del backend está en el sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))

from app import create_app, db
from app.roles.models import Role, RoleSlug
from app.roles.service import RoleService
from app.areas.models import Area
from app.rooms.models import Room
from app.settings.models import SystemSetting
from app.settings.service import SettingsService
from app.calendar.service import WorkScheduleService
from app.users.models import User


# ─── Seeders individuales ────────────────────────────────────────────────────

def seed_roles():
    """Inserta los 3 roles del sistema. Idempotente."""
    before = Role.query.count()
    roles = RoleService.seed_defaults()
    created = max(Role.query.count() - before, 0)
    for role in roles:
        print(f"  [=] Rol disponible: {role.slug}")
    print(f"  → {created} roles creados.\n")


def seed_demo_users():
    """
    Crea los 3 usuarios demo del sistema.
    Contraseñas hasheadas con bcrypt.
    ⚠️ Cambiar en producción inmediatamente.
    """
    from flask_bcrypt import Bcrypt
    from flask import current_app
    bcrypt = Bcrypt(current_app._get_current_object())

    users_data = [
        {
            "email": "admin@ecuamatriz.local",
            "first_name": "Administrador",
            "last_name": "Sistema",
            "role_slug": RoleSlug.ADMIN,
            "position": "Administrador del Sistema",
            "area_name": None,
            "password_env": "SEED_ADMIN_PASSWORD",
            "password_default": "Admin2024!",
        },
        {
            "email": "secretaria@ecuamatriz.local",
            "first_name": "Secretaria",
            "last_name": "Institucional",
            "role_slug": RoleSlug.SECRETARY,
            "position": "Secretaría General",
            "area_name": "Administración",
            "password_env": "SEED_SECRETARY_PASSWORD",
            "password_default": "Secre2024!",
        },
        {
            "email": "usuario@ecuamatriz.local",
            "first_name": "Usuario",
            "last_name": "Demo",
            "role_slug": RoleSlug.USER,
            "position": "Colaborador",
            "area_name": "Sistemas",
            "password_env": "SEED_USER_PASSWORD",
            "password_default": "Usuario2024!",
        },
    ]

    created = 0
    for data in users_data:
        if User.query.filter_by(email=data["email"]).first():
            print(f"  [=] Usuario ya existe: {data['email']}")
            continue

        role = Role.query.filter_by(slug=data["role_slug"]).first()
        if not role:
            print(f"  [!] Rol '{data['role_slug']}' no encontrado. Ejecutar seed_roles primero.")
            continue

        area = None
        if data["area_name"]:
            area = Area.query.filter_by(name=data["area_name"]).first()

        password = os.getenv(data["password_env"], data["password_default"])
        user = User(
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
            role_id=role.id,
            area_id=area.id if area else None,
            position=data["position"],
            is_active=True,
        )
        db.session.add(user)
        created += 1
        print(f"  [+] Usuario creado: {data['email']} (rol: {data['role_slug']})")

    db.session.commit()
    if created:
        print(f"  [!] CAMBIAR CONTRASEÑAS DEMO ANTES DE USAR EN PRODUCCIÓN.")
    print(f"  → {created} usuarios creados.\n")


def seed_areas():
    """Crea áreas organizacionales base. Idempotente."""
    areas = [
        "Administración",
        "Producción",
        "Ventas",
        "Sistemas",
        "Talento Humano",
        "Gerencia",
    ]

    created = 0
    for name in areas:
        if not Area.query.filter_by(name=name).first():
            db.session.add(Area(name=name))
            created += 1
            print(f"  [+] Área: {name}")

    db.session.commit()
    print(f"  → {created} áreas creadas.\n")


def seed_rooms():
    """Crea salas de reunión base. Idempotente."""
    rooms = [
        {
            "name": "Sala Principal",
            "capacity": 15,
            "location": "Piso 2",
            "has_projector": True,
            "has_video_conference": True,
            "description": "Sala principal para reuniones de directorio y eventos importantes.",
        },
        {
            "name": "Sala Reuniones 1",
            "capacity": 8,
            "location": "Piso 1",
            "has_projector": True,
            "has_video_conference": False,
            "description": "Sala de reuniones de tamaño medio.",
        },
        {
            "name": "Sala Reuniones 2",
            "capacity": 6,
            "location": "Piso 1",
            "has_projector": False,
            "has_video_conference": False,
            "description": "Sala pequeña para reuniones de equipo.",
        },
    ]

    created = 0
    for data in rooms:
        if not Room.query.filter_by(name=data["name"]).first():
            db.session.add(Room(**data))
            created += 1
            print(f"  [+] Sala: {data['name']} (cap. {data['capacity']})")

    db.session.commit()
    print(f"  → {created} salas creadas.\n")


def seed_system_settings():
    """
    Inserta configuración del sistema por defecto.
    Parámetros editables por Admin desde el panel sin tocar código.
    Idempotente.
    """
    before = SystemSetting.query.count()
    settings = SettingsService.seed_defaults()
    created = max(SystemSetting.query.count() - before, 0)
    for setting in settings:
        print(f"  [=] Setting disponible: {setting.key} = {setting.value}")
    print(f"  → {created} configuraciones creadas.\n")


def seed_work_schedules():
    """Crea horario laboral base lunes-viernes 08:00-17:00."""
    schedules = WorkScheduleService.seed_defaults()
    for schedule in schedules:
        state = "laborable" if schedule.is_working_day else "no laborable"
        print(f"  [=] Día {schedule.weekday}: {state}")
    print("  → horarios laborales verificados.\n")


# ─── Ejecutor principal ───────────────────────────────────────────────────────

def run_all_seeders():
    """Ejecuta todos los seeders en el orden correcto."""
    app = create_app()

    with app.app_context():
        print("=" * 62)
        print("  AGENDA ECUAMATRIZ — Seeder Inicial")
        print("=" * 62)
        print(f"  BD: {app.config['SQLALCHEMY_DATABASE_URI']}\n")

        print("[1/6] Roles del sistema...")
        seed_roles()

        print("[2/6] Áreas organizacionales...")
        seed_areas()

        print("[3/6] Salas de reunión...")
        seed_rooms()

        print("[4/6] Usuarios demo...")
        seed_demo_users()

        print("[5/6] Configuración del sistema...")
        seed_system_settings()

        print("[6/6] Horario laboral...")
        seed_work_schedules()

        print("=" * 62)
        print("  ✓ Seeder completado exitosamente.")
        print("  Usuarios demo:")
        print("    admin@ecuamatriz.local       → rol: admin")
        print("    secretaria@ecuamatriz.local  → rol: secretaria")
        print("    usuario@ecuamatriz.local     → rol: usuario")
        print("  ⚠  CAMBIAR CONTRASEÑAS ANTES DE PRODUCCIÓN.")
        print("=" * 62)


if __name__ == "__main__":
    run_all_seeders()
