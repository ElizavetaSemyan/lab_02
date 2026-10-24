class StreamStatsError(Exception):
    """Общая ошибка"""


class UnsupportedFormatError(StreamStatsError):
    """Неподдерживаемый формат файла"""


class InvalidEventError(StreamStatsError):
    """Некорректная структура или данные в событии"""


class InvalidTimestampError(StreamStatsError):
    """Некорректное время"""


class CLIConfigError(StreamStatsError):
    """Некорректные аргументы командной строки"""
