import numpy as np
import networkx as nx  # type: ignore
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch
from networkx.drawing.layout import spring_layout
from networkx.algorithms.planarity import check_planarity
from networkx.algorithms.planar_drawing import combinatorial_embedding_to_pos
from depender.render.render import GraphRenderer
from depender.graph.graph import Graph
from typing import Optional


class DependencyRenderer(GraphRenderer):
    def show_or_save_figure(self, filename: Optional[str] = None, transparent: bool = True) -> None:
        if self.output_format is None:
            plt.show()
        else:
            output_path = Path(self.output_dir, filename + "." + self.output_format)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(output_path, dpi=self.dpi, transparent=transparent)

    def render_graph(self, graph: Graph) -> None:
        fig, ax = plt.subplots(figsize=(self.figure_dimensions[0]/self.dpi,
                                        self.figure_dimensions[1]/self.dpi),
                               dpi=self.dpi)
        ax.axis("off")
        nx_graph = nx.DiGraph(graph.edges)
        is_planar, embedding = check_planarity(nx_graph)
        if is_planar:
            positions = combinatorial_embedding_to_pos(embedding)
        else:
            positions = spring_layout(nx_graph, k=0.5, iterations=30)
        self.draw_nodes(graph, positions)
        self.draw_edges(graph, positions)
        # Adjust the figure to show everything
        fig.tight_layout()
        self.show_or_save_figure("dependency_graph")

    def render_matrix(self, graph: Graph):
        fig, ax = plt.subplots(figsize=(self.figure_dimensions[0]/self.dpi,
                                        self.figure_dimensions[1]/self.dpi),
                               dpi=self.dpi)
        node_names = graph.get_all_node_names()
        node_count = graph.node_count()

        for i, node in enumerate(graph.nodes_iter()):
            node.index = i

        matrix = np.zeros((node_count, node_count), dtype=int)
        for source, sink in graph.edges_iter():
            matrix[graph.get_node(source).index, graph.get_node(sink).index] += 1
            # matrix[graph.get_node(sink).index, graph.get_node(source).index] -= 1

        cmap = plt.get_cmap("coolwarm")
        ax.matshow(matrix,
                   cmap=cmap,
                   aspect="equal",
                   origin="upper",
                   alpha=0.7)
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
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=60, ha="left", rotation_mode="anchor")
        # Adjust the figure to show everything
        fig.tight_layout()
        self.show_or_save_figure("dependency_matrix")

    def draw_nodes(self, graph: Graph, positions: dict, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        node_x, node_y = zip(*positions.values())
        node_sizes = list()
        node_colors = list()
        base_size = 40

        for node in positions.keys():
            degree = graph.out_degree(node) - graph.in_degree(node)
            size_multiplier = abs(degree)
            node_colors.append(degree)
            node_size = base_size * (1 + size_multiplier)
            node_sizes.append(node_size)
            graph.get_node(node).size = node_size

        cmap = plt.get_cmap("coolwarm")
        node_scatter = ax.scatter(node_x, node_y,
                                  s=node_sizes,
                                  c=node_colors,
                                  cmap=cmap,
                                  alpha=0.7)
        node_scatter.set_zorder(2)

    def draw_edges(self, graph: Graph, positions: dict, ax=None) -> None:
        if ax is None:
            ax = plt.gca()
        edge_positions = [(positions[e[0]], positions[e[1]]) for e in graph.edges_iter()]
        edge_positions = np.asarray(edge_positions)
        edge_collection = list()
        for (source_name, sink_name), (source, sink) in zip(graph.edges_iter(), edge_positions):
            x1, y1 = source
            x2, y2 = sink
            edge_start_offset = np.sqrt(graph.get_node(source_name).size) / 2
            edge_end_offset = np.sqrt(graph.get_node(sink_name).size) / 2
            arrow = FancyArrowPatch((x1, y1), (x2, y2),
                                    arrowstyle="->",
                                    mutation_scale=10,
                                    shrinkA=edge_start_offset,
                                    shrinkB=edge_end_offset,
                                    alpha=0.7,
                                    zorder=1)
            edge_collection.append(arrow)
            ax.add_patch(arrow)

