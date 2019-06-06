import numpy as np
from pathlib import Path
from matplotlib import cm
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from depender.graph.layout import layout_structure_graph
from depender.render.render import GraphRenderer
from depender.graph.graph import StructureGraph
from typing import Optional


class StructureRenderer(GraphRenderer):
    def __init__(self, base_width: float = 0.3, base_height: float = 0.2,
                 base_font_size: float = 4, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_width = base_width
        self.base_height = base_height
        self.base_font_size = base_font_size
        self.cmap = cm.get_cmap("summer")

    def show_or_save_figure(self, filename: Optional[str] = None, transparent: bool = True) -> None:
        if self.output_format is None:
            plt.show()
        else:
            output_path = Path(self.output_dir, filename + "." + self.output_format)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=self.dpi*10, transparent=transparent)

    def render_graph(self, graph: StructureGraph) -> None:
        fig, ax = plt.subplots(figsize=(self.figure_dimensions[0]/self.dpi,
                                        self.figure_dimensions[1]/self.dpi),
                               dpi=self.dpi)
        ax.axis("off")
        self.render_nodes(graph)
        self.render_edges(graph)
        self.show_or_save_figure("structure_graph")

    def render_nodes(self, graph: StructureGraph, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        fig = plt.gcf()
        text_boxes = list()
        display_to_data = ax.transData.inverted()
        for node in graph.nodes_iter():
            if node.type == "root":
                color = self.cmap(0.2)
            elif node.type == "directory":
                color = self.cmap(0.5)
            else:
                color = self.cmap(0.8)
            text_box = ax.text(node.x, node.y, s=node.label,
                               fontsize=self.base_font_size,
                               horizontalalignment="center",
                               verticalalignment="center",
                               bbox={"facecolor": color, "alpha": 0.7},
                               zorder=2)
            text_boxes.append(text_box)
        fig.canvas.draw()
        height = None
        for text_box, node in zip(text_boxes, graph.nodes_iter()):
            extents = text_box.get_bbox_patch().get_extents().get_points()
            extents = display_to_data.transform(extents)
            if height is None:
                height = extents[1, 1] - extents[0, 1]
            node.width, node.height = extents[1, 0] - extents[0, 0], height
        layout_structure_graph(graph, 0, 0)
        x, y = zip(*[(node.x, node.y) for node in graph.nodes_iter()])
        min_x, max_x = min(x), max(x)
        min_y, max_y = min(y), max(y)
        for node in graph.nodes_iter():
            node.x = (node.x - min_x) / (max_x - min_x)
            node.y = - node.y / min_y + 1
        for text_box, node in zip(text_boxes, graph.nodes_iter()):
            text_box.set_position((node.x, node.y))
        ax.set_xlim((0.0, 1.0))
        ax.set_ylim((-0.1, 1.1))

    def render_edges(self, graph: StructureGraph, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        edge_positions = list()
        for source, sink in graph.edges_iter():
            source_node = graph.get_node(source)
            sink_node = graph.get_node(sink)
            start = (source_node.x, source_node.y - source_node.height / 2)
            end = (source_node.x, (source_node.y + sink_node.y) / 2)
            edge_positions += [(start, end)]
            start = end
            if source_node.x != sink_node.x:
                end = (sink_node.x, end[1])
                edge_positions += [(start, end)]
                start = end
            end = (sink_node.x, sink_node.y + sink_node.height / 2)
            edge_positions += [(start, end)]

        edge_positions = list(set(edge_positions))
        edge_positions = np.asarray(edge_positions)

        edge_collection = LineCollection(edge_positions, colors=self.cmap(0))
        edge_collection.set_zorder(1)
        ax.add_collection(edge_collection)




