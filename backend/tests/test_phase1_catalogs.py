import pytest

from app.areas.service import AreaService
from app.rooms.service import RoomService


def test_create_area_and_avoid_duplicates(db_session):
    area = AreaService.create_area({"name": "Calidad", "description": "Control"})
    assert area.id is not None
    with pytest.raises(ValueError):
        AreaService.create_area({"name": "calidad"})


def test_area_activate_deactivate(db_session):
    area = AreaService.create_area({"name": "Compras"})
    AreaService.set_active(area.id, False)
    assert area.is_active is False
    AreaService.set_active(area.id, True)
    assert area.is_active is True


def test_create_room_capacity_and_duplicate_validation(db_session):
    room = RoomService.create_room({"name": "Sala Calidad", "capacity": 5})
    assert room.capacity == 5
    with pytest.raises(ValueError):
        RoomService.create_room({"name": "Sala Mala", "capacity": 0})
    with pytest.raises(ValueError):
        RoomService.create_room({"name": "sala calidad", "capacity": 4})


def test_room_activate_deactivate(db_session):
    room = RoomService.create_room({"name": "Sala Temporal", "capacity": 3})
    RoomService.set_active(room.id, False)
    assert room.is_active is False
    RoomService.set_active(room.id, True)
    assert room.is_active is True
