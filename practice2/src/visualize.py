"""Визуализация графа: текст на языке Graphviz (DOT), SVG и ASCII-дерево."""

import os
import shutil
import subprocess

ROOT_COLOR = "#ffe699"
CYCLE_COLOR = "red"


class DiagramError(Exception):
    """Ошибка построения изображения."""


def quote(text):
    """Строка в кавычках для DOT."""
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


def cycle_edges(cycles):
    """Множество рёбер (откуда, куда), входящих в циклы."""
    result = set()
    for cycle in cycles:
        for start, end in zip(cycle, cycle[1:]):
            result.add((start, end))
    return result


def to_dot(graph, cycles=()):
    """Текстовое представление графа на языке диаграмм Graphviz."""
    in_cycle = cycle_edges(cycles)
    lines = [
        "digraph dependencies {",
        "    rankdir=LR;",
        '    node [shape=box, style="rounded,filled", fillcolor=white, '
        'fontname="Helvetica"];',
        '    edge [color="#555555"];',
    ]
    for node in graph.nodes():
        attrs = []
        if node == graph.root:
            attrs.append(f'fillcolor="{ROOT_COLOR}"')
            attrs.append("penwidth=2")
        if node in graph.truncated:
            attrs.append('style="rounded,filled,dashed"')
        suffix = f" [{', '.join(attrs)}]" if attrs else ""
        lines.append(f"    {quote(node)}{suffix};")
    for node, children in graph.edges.items():
        for child in children:
            suffix = ""
            if (node, child) in in_cycle:
                suffix = f" [color={CYCLE_COLOR}, penwidth=2]"
            lines.append(f"    {quote(node)} -> {quote(child)}{suffix};")
    lines.append("}")
    return "\n".join(lines) + "\n"


def render_svg(dot_text, svg_path):
    """Сохраняет DOT-файл рядом с SVG и вызывает Graphviz (dot -Tsvg).

    Возвращает путь к DOT-файлу.
    """
    dot_path = os.path.splitext(svg_path)[0] + ".dot"
    try:
        with open(dot_path, "w", encoding="utf-8") as file:
            file.write(dot_text)
    except OSError as error:
        raise DiagramError(f"не удалось записать '{dot_path}': {error}") from error
    program = shutil.which("dot")
    if program is None:
        raise DiagramError(
            "не найдена программа dot из пакета Graphviz "
            "(установите: winget install graphviz / apt install graphviz)"
        )
    result = subprocess.run(
        [program, "-Tsvg", dot_path, "-o", svg_path],
        capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise DiagramError(f"Graphviz завершился с ошибкой: {result.stderr.strip()}")
    return dot_path


def ascii_tree(graph):
    """Строки ASCII-дерева зависимостей.

    (цикл) — узел уже есть на пути от корня; (см. выше) — поддерево уже
    выведено; (...) — узел не раскрыт из-за ограничения глубины.
    """
    lines = [graph.root]
    expanded = {graph.root}

    def walk(node, prefix, path):
        children = graph.edges.get(node, [])
        for index, child in enumerate(children):
            last = index == len(children) - 1
            branch = "`-- " if last else "|-- "
            mark = ""
            if child in path:
                mark = " (цикл)"
            elif child in expanded and graph.edges.get(child):
                mark = " (см. выше)"
            elif child in graph.truncated:
                mark = " (...)"
            lines.append(prefix + branch + child + mark)
            if not mark and child not in expanded:
                expanded.add(child)
                walk(child, prefix + ("    " if last else "|   "), path | {child})

    walk(graph.root, "", {graph.root})
    return lines
