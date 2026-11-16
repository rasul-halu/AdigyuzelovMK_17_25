"""Визуализатор графа зависимостей npm-пакетов (вариант 1).

Запуск: python src/main.py [config.xml]
"""

import argparse
import sys

from config import ConfigError, load_config
from npm_registry import NpmRegistry, RepoError

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


def run(args):
    """Выводит прямые зависимости пакета из npm-репозитория."""
    config = load_config(args.config)
    if config.test_mode:
        raise RepoError("тестовый режим пока не поддерживается (этап 3)")
    registry = NpmRegistry(config.repository)
    version, deps = registry.direct_dependencies(config.package, config.version)
    print(f"Прямые зависимости {config.package}@{version}: {len(deps)}")
    for name, spec in deps.items():
        print(f"  {name}: {spec}")


def main(argv=None):
    """Точка входа, возвращает код завершения."""
    args = parse_args(argv)
    try:
        run(args)
    except (ConfigError, RepoError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
