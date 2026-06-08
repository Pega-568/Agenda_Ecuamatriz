"""Servicios de salas."""

from app import db
from app.rooms.models import Room


class RoomService:
    @staticmethod
    def _validate_capacity(capacity: int):
        if int(capacity) <= 0:
            raise ValueError("La capacidad debe ser positiva.")

    @staticmethod
    def create_room(data: dict) -> Room:
        name = data["name"].strip()
        if Room.query.filter(Room.name.ilike(name)).first():
            raise ValueError("La sala ya existe.")
        RoomService._validate_capacity(data["capacity"])
        room = Room(
            name=name,
            location=data.get("location"),
            capacity=int(data["capacity"]),
            description=data.get("description"),
            has_projector=bool(data.get("has_projector", False)),
            has_video_conference=bool(data.get("has_video_conference", False)),
            is_active=data.get("is_active", True),
        )
        db.session.add(room)
        db.session.commit()
        return room

    @staticmethod
    def update_room(room_id: int, data: dict) -> Room:
        room = db.session.get(Room, room_id)
        if not room:
            raise ValueError("Sala no encontrada.")
        if "name" in data:
            name = data["name"].strip()
            existing = Room.query.filter(Room.name.ilike(name), Room.id != room.id).first()
            if existing:
                raise ValueError("La sala ya existe.")
            room.name = name
        if "capacity" in data:
            RoomService._validate_capacity(data["capacity"])
            room.capacity = int(data["capacity"])
        for field in ["location", "description", "has_projector", "has_video_conference", "is_active"]:
            if field in data:
                setattr(room, field, data[field])
        db.session.commit()
        return room

    @staticmethod
    def set_active(room_id: int, is_active: bool) -> Room:
        return RoomService.update_room(room_id, {"is_active": is_active})

    @staticmethod
    def list_active() -> list[Room]:
        return Room.query.filter_by(is_active=True).order_by(Room.name.asc()).all()

    @staticmethod
    def to_dict(room: Room) -> dict:
        return {
            "id": room.id,
            "name": room.name,
            "location": room.location,
            "capacity": room.capacity,
            "description": room.description,
            "is_active": room.is_active,
            "created_at": room.created_at.isoformat() if room.created_at else None,
            "updated_at": room.updated_at.isoformat() if room.updated_at else None,
        }
