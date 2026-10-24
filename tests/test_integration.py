import json
import subprocess
from pathlib import Path

from streamstats.__main__ import stream_all_files


def test_multiple_files(tmp_path: Path) -> None:
    """Чтение данных из нескольких файлов подряд"""
    file1 = tmp_path / "log1.jsonl"
    file2 = tmp_path / "log2.jsonl"

    file1.write_text('{"timestamp": "2026-10-20T12:00:00", "level": "INFO", "source": "a", "message": "1"}\n')
    file2.write_text('{"timestamp": "2026-10-20T12:01:00", "level": "ERROR", "source": "b", "message": "2"}\n')

    errors_counter: dict[str, int] = {"skipped": 0}

    paths = [str(file1), str(file2)]

    events = list(stream_all_files(paths, "jsonl", False, errors_counter))

    assert len(events) == 2


def test_cli_integration(tmp_path: Path) -> None:
    """Запуск программы через консоль"""
    log_file = tmp_path / "logs.csv"
    log_file.write_text("timestamp,level,source,message\n2026-10-20T12:00:00Z,INFO,app,test\n")
    report_file = tmp_path / "REPORT.json"

    result = subprocess.run([
        "python", "-m", "streamstats", "analyze",
        str(log_file),
        "--format", "csv",
        "--output", str(report_file)
    ], check=False)

    assert result.returncode == 0
    assert report_file.exists()


    with open(report_file, "r", encoding="utf-8") as f:
        report_data = json.load(f)

    assert report_data["total_events"] == 1
    assert report_data["level_counts"]["INFO"] == 1