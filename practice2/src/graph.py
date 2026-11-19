"""Граф зависимостей: построение обходом в ширину (BFS) с рекурсией,
поиск циклов и порядок загрузки.
"""

from dataclasses import dataclass, field


@dataclass
class DependencyGraph:
    """Результат анализа зависимостей.

    edges — узел и список его зависимостей, depth — уровень узла при
    обходе в ширину, truncated — узлы, не раскрытые из-за max_depth,
    warnings — предупреждения источника данных.
    """

    root: str
    edges: dict = field(default_factory=dict)
    depth: dict = field(default_factory=dict)
    truncated: set = field(default_factory=set)
    warnings: list = field(default_factory=list)

    def nodes(self):
        """Узлы в порядке обнаружения (порядок BFS)."""
        return list(self.edges)

    def edge_count(self):
        """Число рёбер."""
        return sum(len(children) for children in self.edges.values())


def build_graph(source, root, max_depth):
    """Строит граф зависимостей пакета root с учётом транзитивности.

    Обход в ширину реализован рекурсивно: функция bfs обрабатывает один
    уровень графа целиком и вызывает себя для следующего уровня.
    Каждый узел раскрывается один раз, поэтому циклы не приводят к
    бесконечному обходу. Узлы на глубине max_depth не раскрываются.
    source.children(node) возвращает (зависимости, предупреждения).
    """
    graph = DependencyGraph(root=root)
    graph.edges[root] = []
    graph.depth[root] = 0

    def bfs(level, depth):
        """Раскрывает уровень level и рекурсивно следующий."""
        if not level:
            return
        if depth >= max_depth:
            graph.truncated.update(level)
            return
        next_level = []
        for node in level:
            children, warnings = source.children(node)
            graph.warnings.extend(warnings)
            graph.edges[node] = children
            for child in children:
                if child not in graph.edges:
                    graph.edges[child] = []
                    graph.depth[child] = depth + 1
                    next_level.append(child)
        bfs(next_level, depth + 1)

    bfs([root], 0)
    return graph


def find_cycles(graph):
    """Ищет циклы: ребро в узел, который лежит на текущем пути обхода.

    Каждый цикл — список узлов, где первый и последний совпадают.
    """
    cycles = []
    visited = set()
    path = []
    on_path = set()

    def visit(node):
        """Обход в глубину с запоминанием пути."""
        visited.add(node)
        path.append(node)
        on_path.add(node)
        for child in graph.edges.get(node, []):
            if child in on_path:
                cycles.append(path[path.index(child):] + [child])
            elif child not in visited:
                visit(child)
        path.pop()
        on_path.discard(node)

    visit(graph.root)
    return cycles


def load_order(graph):
    """Порядок загрузки: каждый пакет идёт после всех своих зависимостей.

    Обратный топологический порядок (обход в глубину, пакет добавляется
    после зависимостей). Ребро, замыкающее цикл, пропускается — пакеты
    цикла загружаются в порядке обхода.
    """
    order = []
    done = set()
    on_path = set()

    def visit(node):
        """Добавляет узел после его зависимостей."""
        on_path.add(node)
        for child in graph.edges.get(node, []):
            if child not in done and child not in on_path:
                visit(child)
        on_path.discard(node)
        done.add(node)
        order.append(node)

    visit(graph.root)
    return order
