from dataclasses import dataclass
from datetime import datetime

from streamstats.errors import InvalidEventError, InvalidTimestampError

ALLOWED_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}




@dataclass
class Event:
    """Хранит данные одной прочитанной строки"""
    timestamp: datetime
    level: str
    source: str
    message: str

def parse_event(row: dict) -> Event:
    """Проверяет словарь из файла, собирает объект event"""

    if not isinstance(row, dict):
        raise InvalidEventError("Запись должна быть словарем")

    for key in ("timestamp", "level", "source", "message"):
        if key not in row:
            raise InvalidEventError("Нет поля:", key)
        if not isinstance(row[key], str):
            raise InvalidEventError(f"Поле {key} должно быть строкой")

    level = row["level"]

    if level not in ALLOWED_LEVELS:
        raise InvalidEventError("Недопустимый уровень:", level)

    source = row["source"].strip()

    if source == "":
        raise InvalidEventError("Пустое поле source")


    time_str = row["timestamp"].strip()

    if time_str == "":
        raise InvalidTimestampError("Пустое поле timestamp")


    try:
        parsed_time = datetime.fromisoformat(time_str)
    except ValueError as err:
        raise InvalidTimestampError("Неверный формат времени:", time_str) from err


    return Event(
        timestamp=parsed_time,
        level=level,
        source=source,
        message=row["message"],
    )