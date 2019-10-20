from networkx import DiGraph, NetworkXException, planar_layout

__all__ = ["DependencyGraph"]


class DependencyGraph(DiGraph):
    def layout(self, **kwargs):
        matrix = kwargs.pop("matrix", True)
        graph = kwargs.pop("graph", False)
        all = kwargs.pop("all", True)
        if all or matrix:
            for i, node in enumerate(self):
                self.nodes[node]["index"] = i
            for (source, sink, _) in self.edges.data():
                if "count" not in self.edges[(source, sink)]:
                    self.edges[(source, sink)]["count"] = 0
                self.edges[(source, sink)]["count"] += 1
        if all or graph:
            try:
                positions = planar_layout(self)
                for node, pos in positions.items():
                    self.nodes[node]["position"] = pos
            except NetworkXException:
                pass
