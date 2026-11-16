"""Тестовый репозиторий: граф зависимостей, описанный в текстовом файле.

Формат файла (пакеты — большие латинские буквы):

    # комментарий
    A: B C
    B: C
    C:
"""

import re

from npm_registry import RepoError

NAME = re.compile(r"^[A-Z]+$")


def parse_line(line, number):
    """Разбирает строку 'A: B C' и возвращает (имя, список зависимостей)."""
    name, separator, rest = line.partition(":")
    name = name.strip()
    if not separator:
        raise RepoError(f"строка {number}: ожидается формат 'A: B C'")
    deps = rest.split()
    for item in [name] + deps:
        if not NAME.match(item):
            raise RepoError(
                f"строка {number}: недопустимое имя пакета '{item}' "
                "(нужны большие латинские буквы)"
            )
    return name, list(dict.fromkeys(deps))


def parse_graph(text):
    """Текст файла -> словарь пакет -> список зависимостей."""
    graph = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.split("#")[0].strip()
        if not line:
            continue
        name, deps = parse_line(line, number)
        if name in graph:
            raise RepoError(f"строка {number}: пакет '{name}' описан повторно")
        graph[name] = deps
    for deps in list(graph.values()):
        for dep in deps:
            graph.setdefault(dep, [])
    return graph


class TestRepository:
    """Источник зависимостей из файла тестового репозитория."""

    __test__ = False  # не путать с тестовым классом unittest/pytest

    def __init__(self, path):
        try:
            with open(path, encoding="utf-8-sig") as file:
                text = file.read()
        except (OSError, UnicodeDecodeError) as error:
            raise RepoError(f"не удалось прочитать файл '{path}': {error}") from error
        self.graph = parse_graph(text)

    def has(self, name):
        """Есть ли пакет в репозитории."""
        return name in self.graph

    def children(self, node):
        """Прямые зависимости пакета и пустой список предупреждений."""
        return list(self.graph.get(node, [])), []
