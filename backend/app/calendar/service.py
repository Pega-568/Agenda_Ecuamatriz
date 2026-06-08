"""Servicios de calendario laboral."""

from datetime import time

from app import db
from app.calendar.models import WorkSchedule


class WorkScheduleService:
    @staticmethod
    def seed_defaults() -> list[WorkSchedule]:
        schedules = []
        for weekday in range(1, 8):
            schedule = WorkSchedule.query.filter_by(weekday=weekday).first()
            if not schedule:
                schedule = WorkSchedule(weekday=weekday)
                db.session.add(schedule)
            if weekday <= 5:
                schedule.is_working_day = True
                schedule.start_time = time(8, 0)
                schedule.end_time = time(17, 0)
            else:
                schedule.is_working_day = False
                schedule.start_time = None
                schedule.end_time = None
            schedules.append(schedule)
        db.session.commit()
        return schedules

    @staticmethod
    def list_schedules() -> list[WorkSchedule]:
        return WorkSchedule.query.order_by(WorkSchedule.weekday.asc()).all()

    @staticmethod
    def update_schedule(weekday: int, data: dict) -> WorkSchedule:
        if weekday < 1 or weekday > 7:
            raise ValueError("weekday debe estar entre 1 y 7.")
        schedule = WorkSchedule.query.filter_by(weekday=weekday).first()
        if not schedule:
            schedule = WorkSchedule(weekday=weekday)
            db.session.add(schedule)

        is_working = bool(data.get("is_working_day", schedule.is_working_day))
        start_time = data.get("start_time", schedule.start_time)
        end_time = data.get("end_time", schedule.end_time)
        if isinstance(start_time, str):
            start_time = WorkScheduleService.parse_time(start_time)
        if isinstance(end_time, str):
            end_time = WorkScheduleService.parse_time(end_time)
        if is_working and (not start_time or not end_time or start_time >= end_time):
            raise ValueError("La hora de inicio debe ser menor que la hora de fin.")

        schedule.is_working_day = is_working
        schedule.start_time = start_time if is_working else None
        schedule.end_time = end_time if is_working else None
        db.session.commit()
        return schedule

    @staticmethod
    def parse_time(value: str) -> time:
        hour, minute = value.split(":", 1)
        return time(int(hour), int(minute))

    @staticmethod
    def to_dict(schedule: WorkSchedule) -> dict:
        return {
            "id": schedule.id,
            "weekday": schedule.weekday,
            "is_working_day": schedule.is_working_day,
            "start_time": schedule.start_time.strftime("%H:%M") if schedule.start_time else None,
            "end_time": schedule.end_time.strftime("%H:%M") if schedule.end_time else None,
        }
