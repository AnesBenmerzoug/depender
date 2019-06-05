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
                 base_font_size: float = 6, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.base_width = base_width
        self.base_height = base_height
        self.base_font_size = base_font_size

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
        coordinate_transformer = ax.transData.inverted()
        cmap = cm.get_cmap("summer")
        for node in graph.nodes_iter():
            if node.type == "root":
                color = cmap(0)
            elif node.type == "directory":
                color = cmap(0.5)
            else:
                color = cmap(1.0)
            text_box = ax.text(node.x, node.y, s=node.label,
                               fontsize=self.base_font_size,
                               horizontalalignment="center",
                               verticalalignment="center",
                               bbox={"facecolor": color},
                               zorder=2)
            fig.canvas.draw()
            extents = coordinate_transformer.transform(text_box.get_bbox_patch().get_extents())
            node.width, node.height = extents[1, 0] - extents[0, 0], extents[1, 1] - extents[0, 1]
            text_boxes.append(text_box)
        layout_structure_graph(graph, 0, 0)
        x, y = zip(*[(node.x, node.y) for node in graph.nodes_iter()])
        for text_box, node in zip(text_boxes, graph.nodes_iter()):
            text_box.set_position((node.x, node.y))
        # ax.set_aspect("equal")
        ax.set_xlim((min(x), max(x)))
        ax.set_ylim((min(y), max(y)))

    def render_edges(self, graph: StructureGraph, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        edge_positions = list()
        for source, sink in graph.edges_iter():
            source_node = graph.get_node(source)
            sink_node = graph.get_node(sink)
            start = (source_node.x, source_node.y)
            end = (source_node.x, (source_node.y + sink_node.y) / 2)
            edge_positions += [(start, end)]
            start = end
            end = (sink_node.x, end[1])
            edge_positions += [(start, end)]
            start = end
            end = (sink_node.x, sink_node.y)
            edge_positions += [(start, end)]

        edge_positions = list(set(edge_positions))
        edge_positions = np.asarray(edge_positions)

        edge_collection = LineCollection(edge_positions)
        edge_collection.set_zorder(1)
        ax.add_collection(edge_collection)




