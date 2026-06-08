"""Servicios de configuracion del sistema."""

from app import db
from app.settings.models import SystemSetting


class SettingsService:
    DEFAULT_SETTINGS = {
        "max_meeting_participants": ("20", "int", "Maximo de participantes por reunion"),
        "max_meeting_duration_minutes": ("240", "int", "Duracion maxima de reunion en minutos"),
        "min_meeting_notice_minutes": ("60", "int", "Anticipacion minima para crear reunion"),
        "allow_meetings_outside_work_hours": ("false", "bool", "Permitir reuniones fuera de horario laboral"),
        "allow_meetings_on_non_working_days": ("false", "bool", "Permitir reuniones en dias no laborables"),
        "qr_valid_before_minutes": ("15", "int", "Minutos antes para validez de QR futuro"),
        "qr_valid_after_minutes": ("30", "int", "Minutos despues para validez de QR futuro"),
        "web_notifications_enabled": ("true", "bool", "Notificaciones web activas"),
        "mobile_notifications_enabled": ("false", "bool", "Notificaciones moviles futuras activas"),
    }

    @staticmethod
    def seed_defaults() -> list[SystemSetting]:
        settings = []
        for key, (value, data_type, description) in SettingsService.DEFAULT_SETTINGS.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                setting = SystemSetting(key=key, value=value, data_type=data_type, description=description)
                db.session.add(setting)
            settings.append(setting)
        db.session.commit()
        return settings

    @staticmethod
    def list_settings() -> list[SystemSetting]:
        return SystemSetting.query.order_by(SystemSetting.key.asc()).all()

    @staticmethod
    def update_settings(values: dict) -> list[SystemSetting]:
        updated = []
        for key, value in values.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                if key not in SettingsService.DEFAULT_SETTINGS:
                    raise ValueError(f"Configuración no permitida: {key}")
                default_value, data_type, description = SettingsService.DEFAULT_SETTINGS[key]
                setting = SystemSetting(key=key, value=default_value, data_type=data_type, description=description)
                db.session.add(setting)
            SettingsService._validate_value(setting.data_type, value, key)
            setting.value = SettingsService._serialize_value(setting.data_type, value)
            updated.append(setting)
        db.session.commit()
        return updated

    @staticmethod
    def _validate_value(data_type: str, value, key: str):
        if data_type == "int" and int(value) < 0:
            raise ValueError(f"{key} debe ser mayor o igual a cero.")
        if data_type == "bool" and str(value).lower() not in ("true", "false", "1", "0", "yes", "no"):
            raise ValueError(f"{key} debe ser booleano.")

    @staticmethod
    def _serialize_value(data_type: str, value) -> str:
        if data_type == "bool":
            return "true" if str(value).lower() in ("true", "1", "yes") else "false"
        return str(value)

    @staticmethod
    def to_dict(setting: SystemSetting) -> dict:
        return {
            "key": setting.key,
            "value": setting.get_typed_value(),
            "raw_value": setting.value,
            "data_type": setting.data_type,
            "description": setting.description,
        }
