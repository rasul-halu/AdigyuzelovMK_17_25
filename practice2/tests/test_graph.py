import unittest

from tests.helpers import data_path, fake_fetch
from graph import build_graph, find_cycles, load_order
from npm_registry import NpmRegistry, RepoError
from test_repo import TestRepository, parse_graph


def repo(name):
    return TestRepository(data_path("data", name))


class TestRepoTest(unittest.TestCase):
    def test_parse(self):
        graph = parse_graph("# c\nA: B C\nB:\n")
        self.assertEqual(graph, {"A": ["B", "C"], "B": [], "C": []})

    def test_errors(self):
        for text in ["A B", "A: b", "A:\nA:"]:
            with self.assertRaises(RepoError):
                parse_graph(text)
        with self.assertRaises(RepoError):
            repo("graph_bad.txt")
        with self.assertRaises(RepoError):
            repo("no_such.txt")


class GraphTest(unittest.TestCase):
    def test_bfs_order_and_depth(self):
        graph = build_graph(repo("graph_simple.txt"), "A", 10)
        self.assertEqual(graph.nodes(), ["A", "B", "C", "D"])
        self.assertEqual(graph.depth, {"A": 0, "B": 1, "C": 1, "D": 2})
        self.assertEqual(graph.edge_count(), 4)
        self.assertEqual(find_cycles(graph), [])

    def test_max_depth(self):
        graph = build_graph(repo("graph_deep.txt"), "A", 2)
        self.assertEqual(graph.nodes(), ["A", "B", "C"])
        self.assertEqual(graph.truncated, {"C"})
        graph = build_graph(repo("graph_deep.txt"), "A", 1)
        self.assertEqual(graph.nodes(), ["A", "B"])

    def test_cycles(self):
        graph = build_graph(repo("graph_cycle.txt"), "A", 10)
        self.assertEqual(find_cycles(graph), [["A", "B", "C", "A"]])
        graph = build_graph(repo("graph_complex.txt"), "A", 10)
        self.assertEqual(find_cycles(graph), [["B", "D", "B"], ["E", "E"]])

    def test_load_order(self):
        graph = build_graph(repo("graph_simple.txt"), "A", 10)
        self.assertEqual(load_order(graph), ["D", "B", "C", "A"])
        graph = build_graph(repo("graph_cycle.txt"), "A", 10)
        self.assertEqual(load_order(graph), ["D", "C", "B", "A"])
        graph = build_graph(repo("graph_complex.txt"), "A", 10)
        order = load_order(graph)
        self.assertEqual(order[-1], "A")
        for node, children in graph.edges.items():
            for child in children:
                if child != node and not (node, child) == ("D", "B"):
                    self.assertLess(order.index(child), order.index(node))

    def test_npm_graph_with_cycle(self):
        registry = NpmRegistry("https://r", fetch=fake_fetch)
        graph = build_graph(registry, "app@2.0.0", 10)
        self.assertEqual(graph.nodes(), ["app@2.0.0", "lib-a@1.2.0",
                                         "lib-b@2.0.5", "lib-c@2.1.0",
                                         "lib-c@1.0.0"])
        self.assertEqual(find_cycles(graph),
                         [["app@2.0.0", "lib-b@2.0.5", "app@2.0.0"]])


if __name__ == "__main__":
    unittest.main()
