import csv
import json


def json_report(stats: dict, output: str) -> None:
    """Сохраняет статистику в json-файл"""

    if stats["first_time"] is not None:
        stats["first_time"] = stats["first_time"].isoformat()

    if stats["last_time"] is not None:
        stats["last_time"] = stats["last_time"].isoformat()


    with open(output, mode="w", encoding="utf-8") as file:
        json.dump(stats, file, indent=4, ensure_ascii=False)




def csv_report(stats: dict, output_path: str) -> None:
    """Генерирует csv-отчет по рассчитанной статистике"""
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Metric", "Value"])
        writer.writerow(["Total Events", stats["total_events"]])
        writer.writerow(["First Timestamp", stats["first_timestamp"]])
        writer.writerow(["Last Timestamp", stats["last_timestamp"]])

        for level, count in stats["levels"].items():
            writer.writerow(["Level:", level, count])

        for source, count in stats["top_errors_sources"]:
            writer.writerow(["Error Source:", source, count])