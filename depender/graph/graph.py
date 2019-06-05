from functools import partial
from collections import defaultdict
from depender.graph.node import Node
from typing import Dict, List, Iterable, Union, Tuple


class Graph:
    def __init__(self) -> None:
        self.nodes = dict()  # type: Dict[str, Node]
        self.edges = defaultdict(partial(defaultdict, dict))  # type: ignore

    def add_node(self, name: str, **kwargs: Union[int, str]) -> None:
        self.nodes[name] = Node(name, **kwargs)

    def remove_node(self, name: str) -> None:
        self.nodes.pop(name, None)

    def node_exists(self, name: str) -> bool:
        return name in self.nodes

    def node_count(self) -> int:
        return len(self.nodes)

    def get_node(self, name: str) -> Node:
        if not self.nodes:
            raise AttributeError("This graph is empty")
        return self.nodes[name]

    def get_all_node_names(self) -> List[str]:
        return list(self.nodes.keys())

    def nodes_iter(self) -> Iterable[Node]:
        for node in self.nodes.values():
            yield node

    def add_edge(self, source: str, sink: str, **kwargs) -> None:
        # Create the nodes if they do not exist yet
        if not self.node_exists(source):
            self.add_node(source)
        if not self.node_exists(sink):
            self.add_node(sink)
        # Create the edge
        self.edges[source][sink] = kwargs

    def remove_edge(self, source: str, sink: str) -> None:
        self.edges[source].pop(sink, None)
        self.edges.pop(source, None)

    def get_edge(self, source: str, sink: str) -> dict:
        return self.edges[source][sink]

    def edge_exists(self, source: str, sink: str) -> bool:
        if source in self.edges:
            return sink in self.edges[source]
        else:
            return False

    def edges_iter(self) -> Iterable[Tuple[str, str]]:
        for source, sinks in self.edges.items():
            for sink in sinks:
                yield source, sink

    def in_degree(self, name: str) -> int:
        in_degree = 0
        for _, sinks in self.edges_iter():
            if name in sinks:
                in_degree += 1
        return in_degree

    def out_degree(self, name: str) -> int:
        return len(self.edges[name])

    def __repr__(self) -> str:
        representation = "( \n"
        for source, sink in self.edges_iter():
            representation += f"{source} ({self.nodes[source].type}) -> {sink} ({self.nodes[sink].type}), \n"
        representation += ")"
        return representation

class StructureGraph(Graph):
    def get_node_children(self, node: str) -> List[Node]:
        return self.nodes[node].children

    def add_edge(self, source: str, sink: str, **kwargs) -> None:
        super().add_edge(source, sink, **kwargs)
        # Add properties to both nodes
        self.nodes[source].children.append(self.nodes[sink])
        self.nodes[sink].parent = self.nodes[source]
        self.nodes[sink].ancestor = self.nodes[sink]
        self.nodes[sink].index = len(self.edges[source])
        # Add siblings
        if len(self.edges[source]) > 1:
            self.nodes[sink].leftmost_sibling = self.nodes[next(iter(self.edges[source].keys()))]
            self.nodes[sink].left_sibling = self.nodes[list(self.edges[source].keys())[-2]]

    def remove_edge(self, source: str, sink: str):
        super().remove_edge(source, sink)

    def get_root_node(self) -> Node:
        if not self.nodes:
            raise AttributeError("This graph is empty")
        return next(iter(self.nodes.values()))
