"""Servicios de areas."""

from app import db
from app.areas.models import Area


class AreaService:
    @staticmethod
    def create_area(data: dict) -> Area:
        name = data["name"].strip()
        if Area.query.filter(Area.name.ilike(name)).first():
            raise ValueError("El área ya existe.")
        area = Area(name=name, description=data.get("description"), is_active=data.get("is_active", True))
        db.session.add(area)
        db.session.commit()
        return area

    @staticmethod
    def update_area(area_id: int, data: dict) -> Area:
        area = db.session.get(Area, area_id)
        if not area:
            raise ValueError("Área no encontrada.")
        if "name" in data:
            name = data["name"].strip()
            existing = Area.query.filter(Area.name.ilike(name), Area.id != area.id).first()
            if existing:
                raise ValueError("El área ya existe.")
            area.name = name
        if "description" in data:
            area.description = data["description"]
        if "is_active" in data:
            area.is_active = bool(data["is_active"])
        db.session.commit()
        return area

    @staticmethod
    def set_active(area_id: int, is_active: bool) -> Area:
        return AreaService.update_area(area_id, {"is_active": is_active})

    @staticmethod
    def list_active() -> list[Area]:
        return Area.query.filter_by(is_active=True).order_by(Area.name.asc()).all()

    @staticmethod
    def to_dict(area: Area) -> dict:
        return {
            "id": area.id,
            "name": area.name,
            "description": area.description,
            "is_active": area.is_active,
            "created_at": area.created_at.isoformat() if area.created_at else None,
            "updated_at": area.updated_at.isoformat() if area.updated_at else None,
        }
