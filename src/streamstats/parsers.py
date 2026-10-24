import csv
import json
import sys
from collections.abc import Iterator

from streamstats.errors import StreamStatsError, UnsupportedFormatError
from streamstats.models import Event, parse_event


def parse_file(path: str, file_format: str, skip_invalid: bool, counts: dict) -> Iterator[Event]:
    """Открывает файл нужным способом и проверяет каждую строку.
    Если с ней что-то не так то либо пропускает её, либо останавливается"""

    if file_format == "csv":
        row_stream = parse_csv(path)
    elif file_format == "jsonl":
        row_stream = parse_jsonl(path)

    else:
        raise UnsupportedFormatError("Формат не поддерживается")

    line_number = 1

    for row in row_stream:
        try:
            event = parse_event(row)
            yield event

        except StreamStatsError as e:

            if skip_invalid:
                print(f"WARNING: Файл {path}, строка {line_number} пропущена. Причина: {e}", file=sys.stderr)
                counts["skipped"] += 1
            else:
                raise StreamStatsError(f"Ошибка в файле {path} на строке {line_number}: {e}")


        line_number += 1



def parse_csv(file_path: str) -> Iterator[dict]:
    """Построчно читает csv"""
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        yield from reader


def parse_jsonl(file_path: str) -> Iterator[dict]:
    """Построчно читает jsonl"""
    with open(file_path, mode="r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line == "":
                continue

            row = json.loads(line)
            yield row