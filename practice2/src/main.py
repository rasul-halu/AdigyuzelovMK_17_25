"""Визуализатор графа зависимостей npm-пакетов (вариант 1).

Запуск: python src/main.py [config.xml] [--load-order]
"""

import argparse
import sys

from config import ConfigError, load_config
from graph import build_graph, find_cycles, load_order
from npm_registry import NpmRegistry, RepoError
from test_repo import TestRepository
from visualize import DiagramError, ascii_tree, render_svg, to_dot

EXIT_OK = 0
EXIT_ERROR = 1


def parse_args(argv=None):
    """Аргументы командной строки: путь к конфигурации и режимы."""
    parser = argparse.ArgumentParser(
        description="Визуализатор графа зависимостей npm-пакетов."
    )
    parser.add_argument(
        "config", nargs="?", default="config.xml",
        help="конфигурационный XML-файл (по умолчанию config.xml)",
    )
    parser.add_argument(
        "--load-order", action="store_true",
        help="вывести порядок загрузки зависимостей",
    )
    return parser.parse_args(argv)


def open_source(config):
    """Источник зависимостей и корневой узел графа."""
    if config.test_mode:
        source = TestRepository(config.repository)
        if not source.has(config.package):
            raise RepoError(f"пакет '{config.package}' не найден в тестовом репозитории")
        return source, config.package
    source = NpmRegistry(config.repository)
    version = source.resolve(config.package, config.version)
    return source, f"{config.package}@{version}"


def print_graph(graph, cycles):
    """Печатает узлы, рёбра и циклы графа."""
    print(
        f"Граф зависимостей {graph.root}: узлов {len(graph.edges)}, "
        f"рёбер {graph.edge_count()}"
    )
    for node, children in graph.edges.items():
        mark = " (не раскрыт: max_depth)" if node in graph.truncated else ""
        print(f"  [{graph.depth[node]}] {node} -> {', '.join(children) or '-'}{mark}")
    if cycles:
        print(f"Циклические зависимости: {len(cycles)}")
        for cycle in cycles:
            print("  " + " -> ".join(cycle))
    else:
        print("Циклические зависимости: нет")
    for warning in graph.warnings:
        print(f"Предупреждение: {warning}", file=sys.stderr)


def print_load_order(graph):
    """Печатает порядок загрузки (зависимости раньше зависящих)."""
    order = load_order(graph)
    print("Порядок загрузки зависимостей:")
    for number, node in enumerate(order, start=1):
        print(f"  {number}. {node}")


def draw(config, graph, cycles):
    """Печатает DOT-текст и сохраняет изображение графа в SVG."""
    text = to_dot(graph, cycles)
    print("Graphviz (DOT):")
    print(text, end="")
    dot_path = render_svg(text, config.output_file)
    print(f"Сохранено: {dot_path}, {config.output_file}")


def run(args):
    """Основная логика; исключения обрабатываются в main."""
    config = load_config(args.config)
    source, root = open_source(config)
    graph = build_graph(source, root, config.max_depth)
    cycles = find_cycles(graph)
    print_graph(graph, cycles)
    if args.load_order:
        print_load_order(graph)
    if config.ascii_tree:
        print("ASCII-дерево:")
        for line in ascii_tree(graph):
            print(line)
    draw(config, graph, cycles)


def main(argv=None):
    """Точка входа, возвращает код завершения."""
    args = parse_args(argv)
    try:
        run(args)
    except (ConfigError, RepoError, DiagramError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return EXIT_ERROR
    return EXIT_OK


if __name__ == "__main__":
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    sys.exit(main())
