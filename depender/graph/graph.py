from functools import partial
from collections import defaultdict
from typing import Any, Dict, List, Iterable, Union, Tuple, Optional


class Node:
    NodeProperties = ["name", "label", "x", "y", "width", "height", "index", "change",
                      "shift", "modifier", "thread", "parent", "ancestor",
                      "leftmost_sibling", "left_sibling", "right_sibling"]

    def __init__(self, name: str, **kwargs: Any) -> None:
        self.name = name  # type: str
        self.label = kwargs.get("label", "")  # type: str
        self.type = kwargs.get("type", None)  # type: Optional[str]
        self.x = kwargs.get("x", 0)  # type: float
        self.y = kwargs.get("y", 0)  # type: float
        self.width = kwargs.get("width", 0)  # type: float
        self.height = kwargs.get("height", 0)  # type: float
        self.index = kwargs.get("index", 1)  # type: int
        self.change = kwargs.get("change", 0)  # type: float
        self.shift = kwargs.get("shift", 0)  # type: float
        self.modifier = kwargs.get("modifier", 0)  # type: float
        self.thread = kwargs.get("thread", None)  # type: Optional[Node]
        self.parent = kwargs.get("parent", None)  # type: Optional[Node]
        self.children = kwargs.get("children", list())  # type: List[Node]
        self.ancestor = kwargs.get("ancestor", self)  # type: Node
        self.leftmost_sibling = kwargs.get("leftmost_sibling", None)  # type: Optional[Node]
        self.left_sibling = kwargs.get("left_sibling", None)  # type: Optional[Node]

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
        self.nodes = dict()  # type: Dict[str, Node]
        self.edges = defaultdict(partial(defaultdict, dict))  # type: ignore

    def add_node(self, name: str, **kwargs: Union[int, str]) -> None:
        if name not in self.nodes:
            self.nodes[name] = Node(name, **kwargs)

    def add_edge(self, source: str, sink: str, **kwargs) -> None:
        # Create the nodes if they do not exist yet
        if not self.node_exists(source):
            self.add_node(source)
        if not self.node_exists(sink):
            self.add_node(sink)
        # Create the edge
        self.edges[source][sink] = kwargs
        # Add properties to both nodes
        self.nodes[source].children.append(self.nodes[sink])
        self.nodes[sink].parent = self.nodes[source]
        self.nodes[sink].ancestor = self.nodes[sink]
        self.nodes[sink].index = len(self.edges[source].keys())
        # Add siblings
        if len(self.edges[source].keys()) > 1:
            self.nodes[sink].leftmost_sibling = self.nodes[next(iter(self.edges[source].keys()))]
            self.nodes[sink].left_sibling = self.nodes[list(self.edges[source].keys())[-2]]

    def get_root_node(self) -> Optional[Node]:
        try:
            return next(iter(self.nodes.values()))
        except StopIteration:
            return None

    def get_node(self, node: str) -> Optional[Node]:
        try:
            return self.nodes[node]
        except KeyError:
            return None

    def get_all_node_names(self) -> List[str]:
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

