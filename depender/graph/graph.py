from functools import partial
from collections import defaultdict
from typing import Any, List, Iterable, Union, Tuple, Optional


class Node:
    NodeProperties = ["name", "label", "x", "y", "index", "change",
                      "shift", "modifier", "thread", "parent", "ancestor",
                      "leftmost_sibling", "left_sibling", "right_sibling"]

    def __init__(self, name: str, **kwargs: Optional[Any]) -> None:
        self.name = name
        self.label = kwargs.get("label", name)
        self.type = kwargs.get("type", None)
        self.x = kwargs.get("x", 0)
        self.y = kwargs.get("y", 0)
        self.index = kwargs.get("index", 1)
        self.change = kwargs.get("change", 0)
        self.shift = kwargs.get("shift", 0)
        self.modifier = kwargs.get("modifier", 0)
        self.thread = kwargs.get("thread", None)
        self.parent = kwargs.get("parent", None)
        self.children = kwargs.get("children", list())
        self.ancestor = kwargs.get("ancestor", name)
        self.leftmost_sibling = kwargs.get("leftmost_sibling", None)
        self.left_sibling = kwargs.get("left_sibling", None)
        self.right_sibling = kwargs.get("right_sibling", None)

    def get_property(self, property: str) -> Optional[Any]:
        try:
            return getattr(self, property)
        except AttributeError:
            return None

    def set_property(self, property: str, value: Any) -> None:
        try:
            setattr(self, property, value)
        except AttributeError:
            pass


class Graph:
    def __init__(self) -> None:
        self.nodes = dict()
        self.edges = defaultdict(partial(defaultdict, dict))

    def add_node(self, name: str, **kwargs: Union[int, str]) -> None:
        self.nodes[name] = Node(name, **kwargs)

    def add_edge(self, source: str, sink: str, **kwargs) -> None:
        # Create the nodes if the do not exist yet
        if not self.node_exists(source):
            self.add_node(source)
        if not self.node_exists(sink):
            self.add_node(sink)
        # Create the edge
        self.edges[source][sink] = kwargs
        #
        self.nodes[source].children.append(self.nodes[sink])
        self.nodes[sink].parent = self.nodes[source]
        self.nodes[sink].ancestor = self.nodes[sink]
        self.nodes[sink].index = len(self.edges[source].keys())
        # Add siblings
        if len(self.edges[source].keys()) > 1:
            self.nodes[sink].leftmost_sibling = self.nodes[next(iter(self.edges[source].keys()))]
            self.nodes[sink].left_sibling = self.nodes[list(self.edges[source].keys())[-2]]
            self.nodes[list(self.edges[source].keys())[-2]].right_sibling = self.nodes[sink]

    def get_node(self, node: str) -> Node:
        return self.nodes[node]

    def get_all_nodes(self) -> List[str]:
        return list(self.nodes.keys())

    def get_node_children(self, node: str) -> List[Node]:
        return self.nodes[node].children

    def node_count(self) -> int:
        return len(self.nodes)

    def node_exists(self, node: str) -> bool:
        return node in self.nodes.keys()

    def nodes_iter(self) -> Iterable[Node]:
        for node in self.nodes.values():
            yield node

    def edges_iter(self) -> Iterable[Tuple[str, dict]]:
        for source, sink in self.edges.items():
            yield source, sink

    def in_degree(self, node: str) -> int:
        in_degree = 0
        for _, sinks in self.edges_iter():
            if node in sinks.keys():
                in_degree += 1
        return in_degree

    def out_degree(self, node: str) -> int:
        return len(self.edges[node])

