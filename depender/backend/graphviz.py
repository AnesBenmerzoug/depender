from io import BytesIO

import graphviz
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from depender.backend.base import BaseBackend
from depender.graph import DependencyGraph, StructureGraph
from matplotlib.colors import to_hex


class GraphivizBackend(BaseBackend):
    def plot_dependency_matrix(self, graph: DependencyGraph, **kwargs):
        graph.layout(matrix=True)
        table = self._create_dependency_table(graph)
        dot = graphviz.Graph(name="Dependency Matrix")
        dot.graph_attr["dpi"] = str(self.dpi)
        dot.node("test", shape="plaintext", label=table)
        dot_str = graphviz.pipe(engine="dot", format="png", data=dot.source.encode())
        # treat the dot output string as an image file
        sio = BytesIO()
        sio.write(dot_str)
        sio.seek(0)
        fig, ax = plt.subplots(
            figsize=(
                self.figure_dimensions[0] / self.dpi,
                self.figure_dimensions[1] / self.dpi,
            ),
            dpi=self.dpi,
        )
        ax.axis("off")
        img = mpimg.imread(sio)
        # plot the image
        ax.imshow(img, aspect="equal")
        fig.tight_layout()
        plt.show()

    def plot_dependency_graph(self, graph: DependencyGraph, **kwargs):
        graph.layout(graph=True)
        dot = graphviz.Digraph(name="Dependency Graph")
        dot.graph_attr["dpi"] = str(self.dpi)
        degrees = {
            node: graph.out_degree(node) - graph.in_degree(node) for node in graph.nodes
        }
        min_degree, max_degree = min(degrees.values()), max(degrees.values())
        cmap = plt.get_cmap("coolwarm")
        for node, degree in degrees.items():
            color = cmap((degree - min_degree) * cmap.N // (max_degree - min_degree))
            color = (*color[:3], 0.7)
            color = to_hex(color, keep_alpha=True)
            dot.node(node, fillcolor=color, style="filled")
        for edge in graph.edges:
            dot.edge(*edge)
        dot_str = graphviz.pipe(engine="dot", format="png", data=dot.source.encode())
        # treat the dot output string as an image file
        sio = BytesIO()
        sio.write(dot_str)
        sio.seek(0)
        fig, ax = plt.subplots(
            figsize=(
                self.figure_dimensions[0] / self.dpi,
                self.figure_dimensions[1] / self.dpi,
            ),
            dpi=self.dpi,
        )
        ax.axis("off")
        img = mpimg.imread(sio)
        # plot the image
        ax.imshow(img, aspect="equal")
        fig.tight_layout()
        plt.show()

    def plot_structure_graph(self, graph: StructureGraph, **kwargs):
        dot = graphviz.Digraph(name="Structure Graph")
        dot.graph_attr["fixedsize"] = "true"
        dot.graph_attr["splines"] = "true"
        cmap = plt.get_cmap("coolwarm")
        for node, attrs in graph.nodes.items():
            if attrs["type"] == "root":
                color = cmap(0.2)
                shape = "folder"
            elif attrs["type"] == "directory":
                color = cmap(0.5)
                shape = "folder"
            else:
                color = cmap(0.8)
                shape = "note"
            color = (*color[:3], 0.7)
            color = to_hex(color, keep_alpha=True)
            dot.node(
                node, label=attrs["label"], shape=shape, fillcolor=color, style="filled"
            )
        for edge in graph.edges:
            dot.edge(*edge)
        dot_str = graphviz.pipe(engine="dot", format="png", data=dot.source.encode())
        # treat the dot output string as an image file
        sio = BytesIO()
        sio.write(dot_str)
        sio.seek(0)
        fig, ax = plt.subplots(
            figsize=(
                self.figure_dimensions[0] / self.dpi,
                self.figure_dimensions[1] / self.dpi,
            ),
            dpi=self.dpi,
        )
        ax.axis("off")
        img = mpimg.imread(sio)
        # plot the image
        ax.imshow(img, aspect="equal")
        fig.tight_layout()
        plt.show()

    def _create_dependency_table(self, graph):
        node_names = list(graph.nodes)
        node_count = graph.number_of_nodes()
        matrix = [[0 for _ in range(node_count)] for _ in range(node_count)]
        max_count = 0
        for (source, sink, values) in graph.edges.data():
            matrix[graph.nodes[source]["index"]][graph.nodes[sink]["index"]] = values[
                "count"
            ]
            max_count = max(max_count, values["count"])
        max_count = max(max_count, 1)
        table = list()
        table.append("<<table>")
        header_str = "<tr><td></td>"
        for name in node_names:
            header_str += "<td>{}</td>".format(name)
        header_str += "</tr>"
        table.append(header_str)
        cmap = plt.get_cmap("coolwarm")
        for i, row in enumerate(matrix):
            row_str = "<tr><td>{}</td>".format(node_names[i])
            for count in row:
                color = cmap(count * cmap.N // max_count)
                color = (*color[:3], 0.7)
                color = to_hex(color, keep_alpha=True)
                row_str += "<td bgcolor='{}'>{}</td>".format(color, count)
            row_str += "</tr>\n"
            table.append(row_str)
        table.append("</table>>")
        return "\n".join(table)
