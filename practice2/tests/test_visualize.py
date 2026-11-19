"""Тесты Graphviz, SVG и ASCII-дерева."""

import os
import shutil
import tempfile
import unittest

from tests.helpers import data_path
from graph import build_graph, find_cycles
from test_repo import TestRepository
from visualize import ascii_tree, find_dot, render_svg, to_dot


def graph_of(name, depth=10):
    """Граф пакета A из файла тестового репозитория."""
    return build_graph(TestRepository(data_path("data", name)), "A", depth)


class VisualizeTest(unittest.TestCase):
    """Текст DOT, поиск Graphviz и ASCII-дерево."""

    def test_dot(self):
        """Корень выделен, рёбра цикла красные."""
        graph = graph_of("graph_cycle.txt")
        text = to_dot(graph, find_cycles(graph))
        self.assertTrue(text.startswith("digraph dependencies {"))
        self.assertIn('"A" [fillcolor="#ffe699", penwidth=2];', text)
        self.assertIn('"C" -> "A" [color=red, penwidth=2];', text)
        self.assertIn('"C" -> "D";', text)

    def test_dot_truncated(self):
        """Нераскрытый узел пунктирный."""
        text = to_dot(graph_of("graph_deep.txt", 1))
        self.assertIn('"B" [style="rounded,filled,dashed"];', text)

    def test_ascii_tree(self):
        """Дерево с пометками цикла и повтора."""
        self.assertEqual(ascii_tree(graph_of("graph_simple.txt")), [
            "A", "|-- B", "|   `-- D", "`-- C", "    `-- D",
        ])
        self.assertEqual(ascii_tree(graph_of("graph_cycle.txt")), [
            "A", "`-- B", "    `-- C", "        |-- A (цикл)", "        `-- D",
        ])
        lines = ascii_tree(graph_of("graph_complex.txt"))
        self.assertIn("|   |-- D", lines)
        self.assertIn("|   |   |-- B (цикл)", lines)
        self.assertIn("    |-- E (см. выше)", lines)
        self.assertEqual(ascii_tree(graph_of("graph_deep.txt", 1)),
                         ["A", "`-- B (...)"])

    def test_find_dot_env(self):
        """Путь к dot из переменной GRAPHVIZ_DOT."""
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        fake = os.path.join(folder, "dot.exe")
        open(fake, "w").close()
        old = os.environ.get("GRAPHVIZ_DOT")
        os.environ["GRAPHVIZ_DOT"] = fake
        try:
            self.assertEqual(find_dot(), fake)
        finally:
            if old is None:
                del os.environ["GRAPHVIZ_DOT"]
            else:
                os.environ["GRAPHVIZ_DOT"] = old

    @unittest.skipUnless(find_dot(), "Graphviz не установлен")
    def test_render_svg(self):
        """Graphviz создаёт SVG-файл."""
        folder = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, folder)
        svg = os.path.join(folder, "g.svg")
        dot_path = render_svg(to_dot(graph_of("graph_simple.txt")), svg)
        self.assertTrue(os.path.isfile(dot_path))
        with open(svg, encoding="utf-8") as file:
            self.assertIn("<svg", file.read())


if __name__ == "__main__":
    unittest.main()
