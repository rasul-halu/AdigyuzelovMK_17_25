"""Визуализатор графа зависимостей npm-пакетов (вариант 1).

Запуск: python src/main.py [config.xml]
"""

import argparse
import sys

from config import ConfigError, load_config

EXIT_OK = 0
EXIT_ERROR = 1


def parse_args(argv=None):
    """Аргументы командной строки: путь к конфигурации."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей npm-пакетов."
    )
    parser.add_argument(
        "config", nargs="?", default="config.xml",
        help="конфигурационный XML-файл (по умолчанию config.xml)",
    )
    return parser.parse_args(argv)


def format_value(value):
    """Значение параметра для вывода."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def main(argv=None):
    """Точка входа, возвращает код завершения."""
    args = parse_args(argv)
    try:
        config = load_config(args.config)
    except ConfigError as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    for key, value in config.items():
        print(f"{key}={format_value(value)}")
    return EXIT_OK


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
