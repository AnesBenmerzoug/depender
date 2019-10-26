import matplotlib.pyplot as plt
import numpy as np
from depender.draw.base import BaseGraphPlot
from depender.graph import DependencyGraph, StructureGraph
from matplotlib import cm
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch


class MatplotlibGraphPlot(BaseGraphPlot):
    def plot_dependency_matrix(self, graph: DependencyGraph, **kwargs):
        graph.layout(matrix=True)
        node_names = graph.nodes()
        node_count = graph.number_of_nodes()

        matrix = [[0 for _ in range(node_count)] for _ in range(node_count)]
        for (source, sink, values) in graph.edges.data():
            matrix[graph.nodes[source]["index"]][graph.nodes[sink]["index"]] = values[
                "count"
            ]
            # matrix[graph.get_node(sink).index, graph.get_node(source).index] -= 1
        cmap = plt.get_cmap("coolwarm")
        fig, ax = plt.subplots(
            figsize=(
                self.figure_dimensions[0] / self.dpi,
                self.figure_dimensions[1] / self.dpi,
            ),
            dpi=self.dpi,
        )
        ax.matshow(matrix, cmap=cmap, aspect="equal", origin="upper", alpha=0.7)
        # Major ticks
        major_tick_locations = np.arange(node_count)
        ax.set_xticks(major_tick_locations)
        ax.set_yticks(major_tick_locations)
        # Tick labels
        ax.set_xticklabels(node_names)
        ax.set_yticklabels(node_names)
        # Add and position labels
        ax.set_xlabel("Imported modules")
        ax.set_ylabel("Importing modules")
        ax.yaxis.set_label_position("right")
        # Set minor ticks and plot grid lines
        ax.set_xticks(major_tick_locations - 0.5, minor=True)
        ax.set_yticks(major_tick_locations - 0.5, minor=True)
        ax.grid(which="minor", color="w", linestyle="-", linewidth=3)
        # Tick parameters and label rotation
        ax.tick_params(axis="both", which="both", length=0, width=0)
        plt.setp(
            ax.xaxis.get_majorticklabels(),
            rotation=60,
            ha="left",
            rotation_mode="anchor",
        )
        # Adjust the figure to show everything
        fig.tight_layout()
        plt.show()

    def plot_dependency_graph(self, graph: DependencyGraph, **kwargs):
        graph.layout(graph=True)
        fig, ax = plt.subplots(
            figsize=(
                self.figure_dimensions[0] / self.dpi,
                self.figure_dimensions[1] / self.dpi,
            ),
            dpi=self.dpi,
        )
        ax.axis("off")
        self._plot_dependency_nodes(graph)
        self._plot_dependency_edges(graph)
        # Adjust the figure to show everything
        fig.tight_layout()
        plt.show()

    def plot_structure_graph(self, graph: StructureGraph, **kwargs):
        fig, ax = plt.subplots(
            figsize=(
                self.figure_dimensions[0] / self.dpi,
                self.figure_dimensions[1] / self.dpi,
            ),
            dpi=self.dpi,
        )
        ax.axis("off")
        self._plot_structure_nodes(graph)
        self._plot_structure_edges(graph)
        plt.show()

    @staticmethod
    def _plot_dependency_nodes(graph: DependencyGraph, ax=None):
        if ax is None:
            ax = plt.gca()
        node_x, node_y = [], []
        for node, value in graph.nodes.items():
            node_x.append(value["position"][0])
            node_y.append(value["position"][1])
        node_sizes = list()
        node_colors = list()
        base_size = 40

        for node in graph.nodes:
            degree = graph.out_degree(node) - graph.in_degree(node)
            size_multiplier = abs(degree)
            node_colors.append(degree)
            node_size = base_size * (1 + size_multiplier)
            node_sizes.append(node_size)
            graph.nodes[node]["size"] = node_size

        cmap = plt.get_cmap("coolwarm")
        node_scatter = ax.scatter(
            node_x, node_y, s=node_sizes, c=node_colors, cmap=cmap, alpha=0.7
        )
        node_scatter.set_zorder(2)

    @staticmethod
    def _plot_dependency_edges(graph: DependencyGraph, ax=None):
        if ax is None:
            ax = plt.gca()
        edge_positions = []
        for (source, sink, _) in graph.edges.data():
            edge_positions.append(
                (graph.nodes[source]["position"], graph.nodes[sink]["position"])
            )
        edge_positions = np.asarray(edge_positions)
        edge_collection = list()
        for (source_name, sink_name), (source, sink) in zip(
            graph.edges(), edge_positions
        ):
            x1, y1 = source
            x2, y2 = sink
            edge_start_offset = np.sqrt(graph.nodes[source_name]["size"]) / 2
            edge_end_offset = np.sqrt(graph.nodes[sink_name]["size"]) / 2
            arrow = FancyArrowPatch(
                (x1, y1),
                (x2, y2),
                arrowstyle="->",
                mutation_scale=10,
                shrinkA=edge_start_offset,
                shrinkB=edge_end_offset,
                alpha=0.7,
                zorder=1,
            )
            edge_collection.append(arrow)
            ax.add_patch(arrow)

    @staticmethod
    def _plot_structure_nodes(graph: StructureGraph, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        fig = plt.gcf()
        text_boxes = list()
        display_to_data = ax.transData.inverted()
        cmap = cm.get_cmap("summer")
        base_font_size: float = 4
        for node_attr in graph.nodes.values():
            if node_attr["type"] == "root":
                color = cmap(0.2)
            elif node_attr["type"] == "directory":
                color = cmap(0.5)
            else:
                color = cmap(0.8)
            text_box = ax.text(
                node_attr["x"],
                node_attr["y"],
                s=node_attr["label"],
                fontsize=base_font_size,
                horizontalalignment="center",
                verticalalignment="center",
                bbox={"facecolor": color, "alpha": 0.7},
                zorder=2,
            )
            text_boxes.append(text_box)
        fig.canvas.draw()
        height = None
        for text_box, node_attr in zip(text_boxes, graph.nodes.values()):
            extents = text_box.get_bbox_patch().get_extents().get_points()
            extents = display_to_data.transform(extents)
            if height is None:
                height = extents[1, 1] - extents[0, 1]
            node_attr["width"] = extents[1, 0] - extents[0, 0]
            node_attr["height"] = height
        # Layout the graph after setting nodes' width and height
        graph.layout()
        x, y = zip(
            *[(node_attr["x"], node_attr["y"]) for node_attr in graph.nodes.values()]
        )
        min_x, max_x = min(x), max(x)
        min_y = min(y)
        for node_attr in graph.nodes.values():
            node_attr["x"] = (node_attr["x"] - min_x) / (max_x - min_x)
            node_attr["y"] = -node_attr["y"] / min_y + 1
        for text_box, node_attr in zip(text_boxes, graph.nodes.values()):
            text_box.set_position((node_attr["x"], node_attr["y"]))
        ax.set_xlim((0.0, 1.0))
        ax.set_ylim((-0.1, 1.1))

    @staticmethod
    def _plot_structure_edges(graph: StructureGraph, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        cmap = cm.get_cmap("summer")
        edge_positions = list()
        for source, sink in graph.edges():
            start = (
                graph.nodes[source]["x"],
                graph.nodes[source]["y"] - graph.nodes[source]["height"] / 2,
            )
            end = (
                graph.nodes[source]["x"],
                (graph.nodes[source]["y"] + graph.nodes[sink]["y"]) / 2,
            )
            edge_positions += [(start, end)]
            start = end
            if graph.nodes[source]["x"] != graph.nodes[sink]["x"]:
                end = (graph.nodes[sink]["x"], end[1])
                edge_positions += [(start, end)]
                start = end
            end = (
                graph.nodes[sink]["x"],
                graph.nodes[sink]["y"] + graph.nodes[sink]["height"] / 2,
            )
            edge_positions += [(start, end)]

        edge_positions = list(set(edge_positions))
        edge_positions = np.asarray(edge_positions)

        edge_collection = LineCollection(edge_positions, colors=cmap(0))
        edge_collection.set_zorder(1)
        ax.add_collection(edge_collection)
