from collections.abc import Iterator

from streamstats.models import Event


def calculate_statistics(events: Iterator[Event]) -> dict:
    """Считает статистику по файлу"""

    all = 0
    level_counts = {}
    source_counts = {}
    error_sources = {}

    first = None
    last = None

    for event in events:
        all += 1

        if event.level not in level_counts:
            level_counts[event.level] = 0
        level_counts[event.level] += 1

        if event.source not in source_counts:
            source_counts[event.source] = 0
        source_counts[event.source] += 1

        if event.level == "ERROR" or event.level == "CRITICAL":
            if event.source not in error_sources:
                error_sources[event.source] = 0
            error_sources[event.source] += 1



        if (first is None) or (event.timestamp < first):
            first = event.timestamp

        if (last is None) or (event.timestamp > last):
            last = event.timestamp


    sorted_errors = sorted(error_sources.items(), key=lambda x: x[1], reverse=True)
    top_5 = dict(sorted_errors[:5])



    return {
        "total_events": all,
        "level_counts": level_counts,
        "source_counts": source_counts,
        "top_5_error_sources": top_5,
        "first_time": first,
        "last_time": last
    }


def filter_events(events: Iterator[Event], level: str | None = None, source: str | None = None) -> Iterator[Event]:
    """Ленивые фильтры потока событий"""
    for event in events:
        if level and event.level != level:
            continue
        if source and event.source != source:
            continue
        yield event