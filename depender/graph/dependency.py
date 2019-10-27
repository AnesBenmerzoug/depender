import warnings

from networkx import DiGraph, NetworkXException, planar_layout

__all__ = ["DependencyGraph"]


class DependencyGraph(DiGraph):
    def layout(self, **kwargs):
        matrix = kwargs.pop("matrix", False)
        graph = kwargs.pop("graph", False)
        if matrix:
            for i, node in enumerate(self):
                self.nodes[node]["index"] = i
            for (source, sink, _) in self.edges.data():
                if "count" not in self.edges[(source, sink)]:
                    self.edges[(source, sink)]["count"] = 0
                self.edges[(source, sink)]["count"] += 1
        if graph:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    positions = planar_layout(self)
                for node, pos in positions.items():
                    self.nodes[node]["position"] = pos
            except NetworkXException:
                pass
