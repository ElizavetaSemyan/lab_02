from pathlib import Path

import pytest

from streamstats.__main__ import filter_events
from streamstats.errors import StreamStatsError
from streamstats.models import Event
from streamstats.parsers import parse_file


def test_bad_line_stops_parsing(tmp_path: Path) -> None:
    """По умолчанию программа выдает ошибку на неправильную строку"""
    log_file = tmp_path / "bad.jsonl"
    log_file.write_text(
        '{"timestamp": "2026-10-20T12:00:00", "level": "INFO", "source": "app", "message": "ok"}\n'
        '{"timestamp": "2026-10-20", "level": "КРИВОЙ_УРОВЕНЬ", "message": "fail"}\n',
        encoding="utf-8"
    )

    errors_counter: dict[str, int] = {"skipped": 0}


    with pytest.raises(StreamStatsError):
        list(parse_file(str(log_file), "jsonl", skip_invalid=False, counts=errors_counter))



def test_skip_invalid_flag(tmp_path: Path) -> None:
    """При флаге --skip-invalid ошибка пропускается, счетчик увеличивается"""
    log_file = tmp_path / "mixed.jsonl"
    log_file.write_text(
        '{"timestamp": "2026-10-20T12:00:00", "level": "INFO", "source": "app", "message": "1"}\n'
        '{"timestamp": "сломанная_дата", "level": "INFO", "source": "app", "message": "2"}\n'
        '{"timestamp": "2026-10-20T12:01:00", "level": "ERROR", "source": "app", "message": "3"}\n',
        encoding="utf-8"
    )

    errors_counter: dict[str, int] = {"skipped": 0}

    events = list(parse_file(str(log_file), "jsonl", skip_invalid=True, counts=errors_counter))

    assert len(events) == 2
    assert events[1].level == "ERROR"
    assert errors_counter["skipped"] == 1



def test_russian_text(tmp_path: Path) -> None:
    """Проверка читаемости русских букв"""
    csv_file = tmp_path / "unicode.csv"
    csv_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-20T12:00:00Z,INFO,источник_1,Всё работает\n"
        "2026-10-20T12:01:00Z,ERROR,сервер,Упал сервер\n",
        encoding="utf-8"
    )

    errors_counter: dict[str, int] = {"skipped": 0}

    events = list(parse_file(str(csv_file), "csv", skip_invalid=False, counts=errors_counter))

    assert len(events) == 2
    assert events[0].source == "источник_1"
    assert events[1].message == "Упал сервер"


def test_empty_file(tmp_path: Path) -> None:
    """Проверка пустого файла"""
    empty_file = tmp_path / "empty.csv"
    empty_file.write_text("", encoding="utf-8")

    errors_counter: dict[str, int] = {"skipped": 0}

    events = list(parse_file(str(empty_file), "csv", skip_invalid=False, counts=errors_counter))

    assert len(events) == 0




def test_filter_events() -> None:
    """Проверка ленивой фильтрации по уровню и источнику"""
    events = [
        Event(timestamp="2026-10-20T12:00", level="INFO", source="app", message="1"),
        Event(timestamp="2026-10-20T12:01", level="ERROR", source="app", message="2"),
        Event(timestamp="2026-10-20T12:02", level="ERROR", source="dbd", message="3")
    ]

    # уровень
    filtered_by_level = list(filter_events(iter(events), level="ERROR"))
    assert len(filtered_by_level) == 2

    # источник
    filtered_by_source = list(filter_events(iter(events), source="db"))
    assert len(filtered_by_source) == 1

    # фильтр + источник
    filtered_by_both = list(filter_events(iter(events), level="INFO", source="app"))
    assert len(filtered_by_both) == 1


def test_unsupported_format(tmp_path: Path) -> None:
    """Проверка генерации ошибки при неизвестном формате файла"""

    log_file = tmp_path / "test.txt"
    log_file.write_text("some data", encoding="utf-8")

    errors_counter: dict[str, int] = {"skipped": 0}

    with pytest.raises(StreamStatsError):
        list(parse_file(str(log_file), "xml", skip_invalid=False, counts=errors_counter))