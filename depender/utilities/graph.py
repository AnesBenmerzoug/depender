from pygraphviz import AGraph

from typing import List, Optional, Iterable


class Graph:
    def __init__(self, strict: bool = False, directed: bool = True,
                 overlap: bool = False, splines: str = "true",
                 rankdir: str = "TB", node_shape: str = "oval",
                 node_style: str = "solid", node_color: str = "black",
                 fontname: str = "Arial") -> None:
        self._graph = AGraph(strict=strict, directed=directed, overlap=overlap, splines=splines, rankdir=rankdir)
        # Set defaults
        graph_defaults = dict(dpi="600!", mindist="4", pad="1", ranksep="0.5", edgsep="5")
        node_defaults = dict(fontsize="14", shape=node_shape, style=node_style, color=node_color, fontname=fontname)
        edge_defaults = dict(color="#1100FF", style="setlinewidth(1)")
        self._graph.graph_attr.update(**graph_defaults)
        self._graph.node_attr.update(**node_defaults)
        self._graph.edge_attr.update(**edge_defaults)

    def add_node(self, name: str, **kwargs: str) -> None:
        self._graph.add_node(n=name, **kwargs)

    def add_edge(self, source: str, sink: Optional[str] = None, label: Optional[str] = None, **kwargs: str) -> None:
        self._graph.add_edge(u=source, v=sink, key=label, **kwargs)

    def add_subgraph(self, nodes: List[str], name: Optional[str] = None, rank: str = "same", **kwargs: str) -> None:
        self._graph.add_subgraph(nbunch=nodes, name=name, rank=rank, **kwargs)

    def add_clusters(self, clusters: dict, penwidth: str = "5") -> None:
        # Add clusters to the graph
        for cluster_name, nodes in clusters.items():
            label = cluster_name[len("cluster_"):]
            self.add_subgraph(nodes, cluster_name, label=label, penwidth=penwidth)

    def get_node(self, name: str) -> AGraph:
        return self._graph.get_node(name)

    def in_degree(self, node) -> int:
        return self._graph.in_degree(node)

    def out_degree(self, node) -> int:
        return self._graph.out_degree(node)

    def nodes_iter(self) -> Iterable:
        return self._graph.nodes_iter()

    def edges_iter(self) -> Iterable:
        return self._graph.edges_iter()

    def layout(self, prog: str = "dot") -> None:
        self._graph.layout(prog=prog)

    def draw(self, path: Optional[str] = None, format: Optional[str] = None, prog: str = "dot") -> None:
        self._graph.draw(path=path, format=format, prog=prog)
