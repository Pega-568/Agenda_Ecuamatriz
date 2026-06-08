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
from app.areas.models import Area
from app.rooms.models import Room
from app.settings.models import SystemSetting
from app.users.models import User


# ─── Seeders individuales ────────────────────────────────────────────────────

def seed_roles():
    """Inserta los 3 roles del sistema. Idempotente."""
    roles_data = [
        {
            "slug": RoleSlug.ADMIN,
            "name": "Administrador",
            "description": (
                "Rol técnico-operativo. Gestiona usuarios, salas, áreas y "
                "configuración del sistema. NO participa en reuniones."
            ),
        },
        {
            "slug": RoleSlug.SECRETARY,
            "name": "Secretaría",
            "description": (
                "Gestiona registros de reuniones, fichas técnicas, reportes y "
                "calendario institucional. No es cuello de botella para reuniones."
            ),
        },
        {
            "slug": RoleSlug.USER,
            "name": "Usuario",
            "description": (
                "Colaborador interno. Puede crear reuniones, buscar participantes, "
                "aceptar/rechazar invitaciones y marcar asistencia por QR."
            ),
        },
    ]

    created = 0
    for data in roles_data:
        if not Role.query.filter_by(slug=data["slug"]).first():
            db.session.add(Role(**data))
            created += 1
            print(f"  [+] Rol creado: {data['slug']}")
        else:
            print(f"  [=] Rol ya existe: {data['slug']}")

    db.session.commit()
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
            "first_name": "Secretaría",
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
        "Gerencia",
        "Producción",
        "Ventas",
        "Sistemas",
        "Talento Humano",
        "Finanzas",
        "Legal",
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
    defaults = [
        # (key, value, data_type, description)
        ("max_participants_per_meeting",        "20",        "int",    "Máximo de participantes por reunión"),
        ("max_meeting_duration_minutes",        "240",       "int",    "Duración máxima de reunión en minutos"),
        ("min_advance_hours",                   "1",         "int",    "Horas mínimas de anticipación para crear reunión"),
        # Horario laboral
        ("work_start_time",                     "08:00",     "string", "Hora inicio jornada laboral (HH:MM)"),
        ("work_end_time",                       "17:00",     "string", "Hora fin jornada laboral (HH:MM)"),
        ("working_days",                        "1,2,3,4,5", "string", "Días laborables: 1=Lun...5=Vie, 6=Sáb, 7=Dom"),
        # Bloqueos
        ("allow_meetings_outside_hours",        "false",     "bool",   "Permitir reuniones fuera del horario laboral"),
        ("allow_meetings_on_non_working_days",  "false",     "bool",   "Permitir reuniones en días no laborables"),
        # QR
        ("qr_valid_minutes_before",             "15",        "int",    "Minutos antes del inicio en que el QR es válido"),
        ("qr_valid_minutes_after",              "30",        "int",    "Minutos después del fin en que el QR sigue válido"),
        # Asistencia manual
        ("allow_manual_attendance_secretary",   "true",      "bool",   "Secretaría puede marcar asistencia manualmente"),
        ("allow_manual_attendance_creator",     "true",      "bool",   "Creador de reunión puede marcar asistencia manualmente"),
        # Notificaciones
        ("notifications_enabled",              "true",      "bool",   "Sistema de notificaciones activado"),
        ("notifications_reminder_minutes",     "30",        "int",    "Minutos antes de la reunión para enviar recordatorio"),
    ]

    created = 0
    for key, value, dtype, desc in defaults:
        if not SystemSetting.query.filter_by(key=key).first():
            db.session.add(SystemSetting(
                key=key,
                value=value,
                data_type=dtype,
                description=desc,
            ))
            created += 1
            print(f"  [+] Setting: {key} = {value}")
        else:
            print(f"  [=] Setting ya existe: {key}")

    db.session.commit()
    print(f"  → {created} configuraciones creadas.\n")


# ─── Ejecutor principal ───────────────────────────────────────────────────────

def run_all_seeders():
    """Ejecuta todos los seeders en el orden correcto."""
    app = create_app()

    with app.app_context():
        print("=" * 62)
        print("  AGENDA ECUAMATRIZ — Seeder Inicial")
        print("=" * 62)
        print(f"  BD: {app.config['SQLALCHEMY_DATABASE_URI']}\n")

        print("[1/5] Roles del sistema...")
        seed_roles()

        print("[2/5] Áreas organizacionales...")
        seed_areas()

        print("[3/5] Salas de reunión...")
        seed_rooms()

        print("[4/5] Usuarios demo...")
        seed_demo_users()

        print("[5/5] Configuración del sistema...")
        seed_system_settings()

        print("=" * 62)
        print("  ✓ Seeder completado exitosamente.")
        print("  Usuarios demo:")
        print("    admin@ecuamatriz.local       → rol: admin")
        print("    secretaria@ecuamatriz.local  → rol: secretary")
        print("    usuario@ecuamatriz.local     → rol: user")
        print("  ⚠  CAMBIAR CONTRASEÑAS ANTES DE PRODUCCIÓN.")
        print("=" * 62)


if __name__ == "__main__":
    run_all_seeders()
