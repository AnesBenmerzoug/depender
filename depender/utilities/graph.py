import os
import numpy as np
import networkx as nx
from functools import partial
from collections import defaultdict
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.models import Circle, Range1d, HoverTool, TapTool, ColumnDataSource
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges, EdgesAndLinkedNodes
from bokeh.models.glyphs import Rect, MultiLine, Text
from bokeh.palettes import Spectral4
from depender.utilities.color import linear_gradient
from jinja2 import Environment, PackageLoader
from typing import List, Union, Tuple, Optional


class Graph:
    def __init__(self) -> None:
        self.node_dict = defaultdict(partial(defaultdict, dict))
        self.edge_dict = defaultdict(partial(defaultdict, dict))
        self.cluster_dict = defaultdict(partial(defaultdict, dict))
        jinja_environment = Environment(loader=PackageLoader("depender", "templates"))
        self.template = jinja_environment.get_template("template.html")

    def add_node(self, name: str, **kwargs) -> None:
        self.node_dict[name] = kwargs

    def add_edge(self, source: str, sink: str, **kwargs) -> None:
        self.edge_dict[source][sink] = kwargs

    def add_subgraph(self, nodes: List[str], name: str, label: str) -> None:
        self.cluster_dict[name]["label"] = label
        self.cluster_dict[name]["nodes"] = nodes

    def add_clusters(self, clusters: dict) -> None:
        # Add clusters to the graph
        for cluster_name, nodes in clusters.items():
            label = cluster_name[len("cluster_"):]
            self.add_subgraph(nodes, cluster_name, label=label)

    def get_node(self, name: str) -> dict:
        return self.node_dict[name]

    def get_nodes(self) -> List[str]:
        return list(self.node_dict.keys())

    def get_node_successors(self, name: str) -> List[str]:
        return list(self.edge_dict[name].keys())

    def get_node_property(self, name: str, property: str) -> Optional[Union[str, int, float]]:
        try:
            return self.node_dict[name][property]
        except KeyError:
            return None

    def set_node_property(self, name: str, property: str, value: Union[str, int, float]) -> None:
        self.node_dict[name][property] = value

    def node_count(self) -> int:
        return len(self.node_dict)

    def node_exists(self, name: str) -> bool:
        return name in self.node_dict.keys()

    def in_degree(self, node: str) -> int:
        in_degree = 0
        for _, sinks in self.edges_iter():
            if node in sinks.keys():
                in_degree += 1
        return in_degree

    def out_degree(self, node: str) -> int:
        return len(self.edge_dict[node])

    def nodes_iter(self) -> Tuple[str, dict]:
        for node, attrs in self.node_dict.items():
            yield node, attrs

    def edges_iter(self) -> Tuple[str, str]:
        for source, sink in self.edge_dict.items():
            yield source, sink

    @staticmethod
    def get_figure(width: int = 800, height: int = 800,
                   tools: str = "pan, wheel_zoom, zoom_in, zoom_out, reset",
                   **kwargs) -> figure:
        plot = figure(plot_width=width,
                      plot_height=height,
                      match_aspect=True,
                      toolbar_location="left",
                      tools=tools,
                      **kwargs)
        plot.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
        plot.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
        plot.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
        plot.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
        plot.xaxis.major_label_text_font_size = "0pt"  # turn off x-axis tick labels
        plot.yaxis.major_label_text_font_size = "0pt"  # turn off y-axis tick labels
        plot.grid.grid_line_color = None
        plot.axis.axis_line_color = None
        plot.axis.major_tick_line_color = None
        plot.toolbar.autohide = True
        plot.toolbar.logo = None
        plot.min_border = 80
        return plot

    def render_graph(self, plot: figure, output_dir: str, output_name: str):
        # Get the script and div elements for the template
        script, div = components(plot)

        # Create the output directory, if it does not exist already, and store the generated html file
        os.makedirs(output_dir, exist_ok=True)

        with open(os.path.join(output_dir, f"{output_name}.html"), "w") as f:
            f.write(self.template.render(script=script, div=div))

    def plot_dependency_graph(self, in_color: str, out_color: str, dis_color: str, output_dir: str) -> None:
        # Create the Networkx directional graph instance from the edge dictionary
        graph = nx.DiGraph(self.edge_dict)
        # Assign names and colors to nodes depending on in and out degrees
        node_attrs = defaultdict(dict)
        for node in self.node_dict.keys():
            in_degree = self.in_degree(node)
            out_degree = self.out_degree(node)
            if in_degree == 0 and out_degree == 0:
                color = dis_color
            else:
                color = linear_gradient(out_color, in_color, in_degree, out_degree)
            node_attrs["color"][node] = color
            node_attrs["name"][node] = node

        nx.set_node_attributes(graph, node_attrs["name"], "node_name")
        nx.set_node_attributes(graph, node_attrs["color"], "node_color")

        # Get a figure
        plot = self.get_figure()
        # Add a hover and a tap tool
        plot.add_tools(HoverTool(tooltips=[("Module Name", "@node_name")]), TapTool())

        # Transfer the graph from networkx to bokeh
        graph_renderer = from_networkx(graph, nx.spring_layout, k=2, scale=5, center=(0, 0))
        # Change the node glyph
        graph_renderer.node_renderer.glyph = Circle(size=30, fill_color="node_color")
        graph_renderer.node_renderer.hover_glyph = Circle(size=30, fill_color=Spectral4[1])
        graph_renderer.node_renderer.selection_glyph = Circle(size=30, fill_color=Spectral4[2])
        # Change the edge glyph
        graph_renderer.edge_renderer.glyph = MultiLine(line_color=Spectral4[0], line_alpha=0.8, line_width=3)
        graph_renderer.edge_renderer.selection_glyph = MultiLine(line_color=Spectral4[2], line_width=3)
        graph_renderer.edge_renderer.hover_glyph = MultiLine(line_color=Spectral4[1], line_width=3)
        # Set the hover and selection behaviour
        graph_renderer.selection_policy = NodesAndLinkedEdges()
        graph_renderer.inspection_policy = NodesAndLinkedEdges()
        plot.renderers.append(graph_renderer)

        # Get the x and y coordinates of all nodes
        x_coordinates, y_coordinates = zip(*graph_renderer.layout_provider.graph_layout.values())

        # Set the x_range and y_range intervals to center the plot
        plot.x_range = Range1d(min(x_coordinates) - 0.2 * abs(min(x_coordinates)),
                               max(x_coordinates) + 0.2 * abs(max(x_coordinates)))
        plot.y_range = Range1d(min(y_coordinates) - 0.2 * abs(min(y_coordinates)),
                               max(y_coordinates) + 0.2 * abs(max(y_coordinates)))

        # Render the graph
        self.render_graph(plot, output_dir, "dependency_graph")

    def plot_dependency_matrix(self, in_color: str, out_color: str, output_dir: str) -> None:
        # Set up the figure
        node_names = list(reversed(self.get_nodes()))
        node_count = self.node_count()
        plot = self.get_figure(x_axis_location="below",
                               x_range=node_names,
                               y_range=node_names)
        plot.add_tools(HoverTool(tooltips=[("Importing Module", "@importing_name"),
                                           ("Imported Module", "@imported_name")]))
        plot.xaxis.axis_label = "Imported Modules"
        plot.yaxis.axis_label = "Importing Module"
        plot.xaxis.major_label_orientation = np.pi / 3
        plot.axis.major_label_text_font_size = "10pt"
        plot.axis.major_label_standoff = 0
        # Add a rectangle glyph to represent the squares of the dependency matrix
        rectangle_size = 0.9
        rectangles = Rect(x="imported_name", y="importing_name",
                          width=rectangle_size, height=rectangle_size,
                          line_color="#8b8a8c", fill_color="color")
        # Assign an index to each node to represent their position in the dependency matrix
        for index, node in enumerate(node_names):
            self.node_dict[node]["index"] = index
        # Create a dictionary that will hold the plot data
        data = dict(importing_name=list(),
                    imported_name=list(),
                    color=list())
        # Create an empty dependency matrix
        matrix = np.zeros((node_count, node_count), dtype=np.int8)
        # Check the dependencies
        for source_node in node_names:
            for sink_node in node_names:
                data["importing_name"].append(source_node)
                data["imported_name"].append(sink_node)
        for source_node, sink_nodes in self.edges_iter():
            for sink_node in sink_nodes:
                matrix[self.node_dict[source_node]["index"], self.node_dict[sink_node]["index"]] += 1
                # matrix[self.node_dict[sink_node]["index"], self.node_dict[source_node]["index"]] += 1
        # Assign colors
        for element in matrix.flatten():
            if element == 0:
                data["color"].append("#ffffff")
            elif element == 1:
                data["color"].append(out_color)
            elif element == -1:
                data["color"].append(in_color)
        # Add the dependency matrix to the data dictionary
        data["matrix"] = matrix.flatten()
        data = ColumnDataSource(data)
        # Add the rectangle glyph to the figure
        plot.add_glyph(data, rectangles)
        # Render the graph
        self.render_graph(plot, output_dir, "dependency_matrix")

    def plot_structure_graph(self, root_dir_color: str, dir_color: str, file_color: str, output_dir: str) -> None:
        width = 1.0
        height = 0.4
        step_x = 2 * width
        step_y = 2.5 * height

        node_data = dict(text_x=list(),
                         text_y=list(),
                         center_x=list(),
                         center_y=list(),
                         width=list(),
                         height=list(),
                         color=list(),
                         name=list(),
                         type=list(),
                         label=list())

        depths = defaultdict(list)
        for node, attrs in self.nodes_iter():
            depths[attrs["depth"]].append(node)

        maximum_depth = max(depths.keys())

        for depth in sorted(depths.keys(), reverse=True):
            count = 0
            for node_name in depths[depth]:
                node = self.get_node(node_name)
                if isinstance(depth, float):
                    node["x"] = self.get_node_property(self.get_node_successors(node_name)[0], "x")
                else:
                    node["x"] = step_x * count
                if node_name in self.edge_dict.keys():
                    children_count = self.get_node_property(node_name, "children_count")
                    count += children_count if children_count is not None else 1
                else:
                    count += 1
                node["y"] = step_y * (maximum_depth - depth)
                node_data["text_x"].append(node["x"])
                node_data["text_y"].append(node["y"])
                node_data["center_x"].append(node["x"])
                node_data["center_y"].append(node["y"])
                node_data["width"].append(0.0 if node["type"] == "point" else width)
                node_data["height"].append(0.0 if node["type"] == "point" else height)
                node_data["name"].append(node["label"])
                node_data["type"].append(node["type"])
                node_data["label"].append(node["label"])
                if node["type"] == "root":
                    node_data["color"].append(root_dir_color)
                elif node["type"] == "directory":
                    node_data["color"].append(dir_color)
                else:
                    node_data["color"].append(file_color)

        edge_data = dict(xs=list(), ys=list())

        for edge_begin, edge_ends in self.edges_iter():
            for edge_end in edge_ends.keys():
                edge_data["xs"].append([self.node_dict[edge_begin]["x"],
                                        self.node_dict[edge_end]["x"]])
                edge_data["ys"].append([self.node_dict[edge_begin]["y"],
                                        self.node_dict[edge_end]["y"]])

        # Get a figure
        plot = self.get_figure(height=600, width=1600)
        # plot.add_tools(HoverTool(tooltips=[("Type", "@type"), ("Path", "@name")]))
        lines = MultiLine(xs="xs", ys="ys", line_color="#8b8a8c")
        rectangles = Rect(x="center_x", y="center_y", width="width", height="height",
                          line_color="#8b8a8c", fill_color="color")
        text = Text(x="text_x", y="text_y", text="label", text_font_size="10pt",
                    text_baseline="middle", text_align="center")

        # Plot the lines connecting the nodes
        edge_data = ColumnDataSource(edge_data)
        plot.add_glyph(edge_data, lines)

        # Plot the nodes on the figure
        node_data = ColumnDataSource(node_data)
        plot.add_glyph(node_data, rectangles)
        plot.add_glyph(node_data, text)

        # Render the graph
        self.render_graph(plot, output_dir, "structure_graph")
