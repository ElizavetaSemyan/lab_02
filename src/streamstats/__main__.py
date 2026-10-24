import argparse
import sys
from collections.abc import Iterator

from streamstats.analysis import calculate_statistics
from streamstats.errors import StreamStatsError
from streamstats.models import Event
from streamstats.parsers import parse_file
from streamstats.report import csv_report, json_report


def parse_args():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(prog="streamstats")

    subparsers = parser.add_subparsers(dest="command", required=True)
    analyze_parser = subparsers.add_parser("analyze")

    analyze_parser.add_argument("inputs", nargs="+", help="Пути к файлам логов")
    analyze_parser.add_argument("--format", choices=["csv", "jsonl"], required=True)
    analyze_parser.add_argument("--output", default="REPORT.json")
    analyze_parser.add_argument("--skip-invalid", action="store_true")

    analyze_parser.add_argument("--filter-level", help="Оставить только события определенного уровня")
    analyze_parser.add_argument("--filter-source", help="Оставить только события конкретного источника")

    return parser.parse_args()


def stream_all_files(file_paths: list[str], file_format: str, skip_invalid: bool, errors_counter: dict):
    """Объединение всех потоков событий из списка файлов"""
    for path in file_paths:
        yield from parse_file(path, file_format, skip_invalid, errors_counter)



def filter_events(events: Iterator[Event], level: str | None = None, source: str | None = None) -> Iterator[Event]:
    """Лениво фильтрует поток событий."""
    for event in events:
        if level and event.level != level:
            continue
        if source and event.source != source:
            continue
        yield event


def main() -> None:
    """Запуск программы"""
    args = parse_args()


    errors_counter = {"skipped": 0}

    try:
        events = stream_all_files(args.inputs, args.format, args.skip_invalid, errors_counter)

        filtered_events = filter_events(events, args.filter_level, args.filter_source)

        stats = calculate_statistics(filtered_events)

        if args.skip_invalid:
            stats["skipped_invalid_rows"] = errors_counter["skipped"]

        if args.output.lower().endswith(".csv"):
            csv_report(stats, args.output)
        else:
            json_report(stats, args.output)

        print("Отчет сохранен:", args.output)


    except (StreamStatsError, OSError) as e:
        print(f"Ошибка: {e}")
        sys.exit(2)





if __name__ == "__main__":
    main()