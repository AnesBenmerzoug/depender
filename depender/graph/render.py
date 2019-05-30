import os
import networkx as nx  # type: ignore
from itertools import chain
from collections import defaultdict
from depender.graph.graph import Graph, Node
from jinja2 import Environment, PackageLoader
from bokeh.models import (Circle, Range1d, HoverTool,
                          TapTool, ColumnDataSource, CategoricalAxis, LinearAxis)  # type: ignore
from bokeh.models.graphs import from_networkx, NodesAndLinkedEdges  # type: ignore
from bokeh.models.glyphs import Square, Rect, MultiLine, Text  # type: ignore
from depender.utilities.color import linear_gradient
from depender.graph.layout import layout_structure_graph
from bokeh.models.callbacks import CustomJS  # type: ignore
from bokeh.palettes import Spectral4  # type: ignore
from bokeh.embed import components  # type: ignore
from bokeh.plotting import figure as Figure  # type: ignore
from bokeh.events import LODStart
from typing import List, Dict, Union, Tuple


class GraphRenderer:
    def __init__(self, in_color: str, out_color: str, dis_color: str, output_dir: str,
                 root_dir_color: str, dir_color: str, file_color: str) -> None:
        self.in_color = in_color
        self.out_color = out_color
        self.dis_color = dis_color
        self.output_dir = output_dir
        self.root_dir_color = root_dir_color
        self.dir_color = dir_color
        self.file_color = file_color
        jinja_environment = Environment(loader=PackageLoader("depender", "templates"))
        self.template = jinja_environment.get_template("template.html")

    @staticmethod
    def get_figure(width: int = 800, height: int = 800,
                   tools: str = "pan, wheel_zoom, zoom_in, zoom_out, reset",
                   **kwargs: Union[int, str, List[str]]) -> Figure:
        figure = Figure(plot_width=width,
                        plot_height=height,
                        match_aspect=True,
                        toolbar_location="left",
                        tools=tools,
                        active_drag="pan",
                        sizing_mode="scale_both",
                        **kwargs)
        figure.xaxis.major_tick_line_color = None  # turn off x-axis major ticks
        figure.xaxis.minor_tick_line_color = None  # turn off x-axis minor ticks
        figure.yaxis.major_tick_line_color = None  # turn off y-axis major ticks
        figure.yaxis.minor_tick_line_color = None  # turn off y-axis minor ticks
        figure.xaxis.major_label_text_font_size = "0pt"  # turn off x-axis tick labels
        figure.yaxis.major_label_text_font_size = "0pt"  # turn off y-axis tick labels
        figure.grid.grid_line_color = None
        figure.axis.axis_line_color = None
        figure.axis.major_tick_line_color = None
        figure.toolbar.autohide = True
        figure.toolbar.logo = None
        figure.min_border = 80
        return figure

    def render_graph(self, plot: Figure, output_dir: str, output_name: str) -> None:
        # Get the script and div elements for the template
        script, div = components(plot)

        # Create the output directory, if it does not exist already, and store the generated html file
        os.makedirs(output_dir, exist_ok=True)

        with open(os.path.join(output_dir, f"{output_name}.html"), "w") as f:
            f.write(self.template.render(script=script, div=div))

    def render_dependency_graph(self, graph: Graph) -> None:
        # Create the Networkx directional graph instance from the edge dictionary
        nx_graph = nx.DiGraph(graph.edges)
        # Assign names and colors to nodes depending on in and out degrees
        node_attrs = defaultdict(dict)  # type: Dict[str, Dict[str, Union[float, str]]]
        for node in graph.get_all_node_names():
            in_degree = graph.in_degree(node)
            out_degree = graph.out_degree(node)
            if in_degree == 0 and out_degree == 0:
                color = self.dis_color
            else:
                color = linear_gradient(self.out_color, self.in_color, in_degree, out_degree)
            node_attrs["color"][node] = color
            node_attrs["name"][node] = node
        nx.set_node_attributes(nx_graph, node_attrs["name"], "node_name")
        nx.set_node_attributes(nx_graph, node_attrs["color"], "node_color")

        # Get a figure
        figure = self.get_figure()
        # Add a hover and a tap tool
        figure.add_tools(HoverTool(tooltips=[("Module Name", "@node_name")]), TapTool())

        # Transfer the graph from networkx to bokeh
        graph_renderer = from_networkx(nx_graph, nx.fruchterman_reingold_layout, k=2, scale=1, center=(0, 0))
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
        figure.renderers.append(graph_renderer)

        # Get the x and y coordinates of all nodes
        try:
            x_coordinates, y_coordinates = zip(*graph_renderer.layout_provider.graph_layout.values())

            # Set the x_range and y_range intervals to center the plot
            figure.x_range = Range1d(min(x_coordinates) - 0.2 * abs(min(x_coordinates)),
                                   max(x_coordinates) + 0.2 * abs(max(x_coordinates)))
            figure.y_range = Range1d(min(y_coordinates) - 0.2 * abs(min(y_coordinates)),
                                   max(y_coordinates) + 0.2 * abs(max(y_coordinates)))
        except ValueError:
            pass

        # Render the graph
        self.render_graph(figure, self.output_dir, "dependency_graph")

    def render_dependency_matrix(self, graph: Graph, base_font_size: int = 1) -> None:
        node_names = list(reversed(graph.get_all_node_names()))
        node_count = graph.node_count()
        rectangle_size = 5.0
        base_font_size = base_font_size
        # Create a dictionary that will hold the figure data
        data = dict(importing_name=list(),
                    imported_name=list(),
                    color=list())  # type: Dict[str, List[Union[str, int]]]
        # Create an empty dependency matrix
        matrix = [[0 for _ in range(node_count)] for _ in range(node_count)]
        data["importing_name"] = list(chain.from_iterable([[name for _ in node_names] for name in node_names]))
        data["imported_name"] = list(chain.from_iterable([[name for name in node_names] for _ in node_names]))
        # Assign an index to each node to represent their position in the dependency matrix
        for index, node in enumerate(node_names):
            graph.get_node(node).index = index  # type: ignore
        for source_node, sink_nodes in graph.edges_iter():
            for sink_node in sink_nodes:
                source_index = graph.get_node(source_node).index
                sink_index = graph.get_node(sink_node).index
                matrix[source_index][sink_index] += 1  # type: ignore
                matrix[sink_index][source_index] += -1  # type: ignore
        # Assign colors
        for element in list(chain.from_iterable(matrix)):
            if element == 0:
                data["color"].append("#ffffff")
            elif element == 1:
                data["color"].append(self.out_color)
            elif element == -1:
                data["color"].append(self.in_color)
        # Add the dependency matrix to the data dictionary
        data["matrix"] = list(chain.from_iterable(matrix))
        data = ColumnDataSource(data)
        # Set up the plot
        figure = self.get_figure(x_range=node_names,
                                 y_range=node_names)
        figure.add_tools(HoverTool(tooltips=[("Importing Module", "@importing_name"),
                                             ("Imported Module", "@imported_name")]))
        figure.xaxis.visible = None
        figure.yaxis.visible = None
        # Creating new axes here in order to set a callback to adapt their font size to the zoom level
        x_axis = LinearAxis(axis_label="Imported Modules",
                            axis_label_standoff=0,
                            major_label_text_font_size=str(base_font_size) + "em")
        x_axis.ticker = list(range(len(node_names)))
        y_axis = CategoricalAxis(axis_label="Importing Module",
                                 axis_label_standoff=0,
                                 major_label_text_font_size=str(base_font_size) + "em",
                                 major_label_overrides=dict(zip(range(len(node_names)), node_names)))

        x_axis.major_tick_line_color = None  # turn off x-axis major ticks
        x_axis.minor_tick_line_color = None  # turn off x-axis minor ticks
        y_axis.major_tick_line_color = None  # turn off y-axis major ticks
        y_axis.minor_tick_line_color = None  # turn off y-axis minor ticks

        figure.add_layout(x_axis, "above")
        figure.add_layout(y_axis, "left")

        axes_label_callback = CustomJS(args=dict(x_axis=x_axis,
                                                 y_axis=y_axis,
                                                 x_range=figure.x_range,
                                                 y_range=figure.y_range,
                                                 base_font_size=base_font_size),
                                       code="""
                    var x_factor = 100 / (x_range.end - x_range.start);
                    var y_factor = 100 / (y_range.end - y_range.start);
                    // x_axis.major_label_text_font_size = base_font_size * x_factor + "em";
                    // y_axis.major_label_text_font_size = base_font_size * y_factor + "em";
                    x_axis.major_label_text_font_size = "100%";
                    y_axis.major_label_text_font_size = "100%";
                    console.log(x_axis.major_label_text_font_size);
                    console.log(y_axis.major_label_text_font_size);
                    x_axis.change.emit();
                    y_axis.change.emit();
                """)
        figure.js_on_event(LODStart, axes_label_callback)
        # Add a square glyph to represent the squares of the dependency matrix
        squares = Square(x="imported_name", y="importing_name",
                         size=rectangle_size, line_color="#8b8a8c", fill_color="color")
        # Add the square glyph to the figure
        figure.add_glyph(data, squares)
        # Render the graph
        self.render_graph(figure, self.output_dir, "dependency_matrix")

    def render_structure_graph(self, graph: Graph,
                               base_width: float = 0.3,
                               base_height: float = 0.2,
                               base_font_size: float = 30) -> None:
        # Layout the node's of the structure to obtain a hierarchical structure
        step_x = base_width * base_font_size / 60
        step_y = base_height * base_font_size * 4 / 10
        layout_structure_graph(graph, step_x, step_y)
        # Iterate over the nodes of the graph to collect data
        node_data = defaultdict(list)  # type: Dict[str, List[Union[None, str, float]]]
        for node in graph.nodes_iter():
            
            node_data["center_x"].append(node.x)
            node_data["center_y"].append(node.y)
            node_data["width"].append(node.width)
            node_data["height"].append(node.height)
            node_data["name"].append(node.label)
            node_data["type"].append(node.type)
            node_data["label"].append(node.label)
            node_data["font_size"].append(base_font_size)
            color = self.root_dir_color if node.type == "root" \
                else self.dir_color if node.type == "directory" \
                else self.file_color
            node_data["color"].append(color)
        node_data = ColumnDataSource(node_data)
        # Iterate over the edges of the graph to collect data
        edge_data = defaultdict(list)  # type: Dict[str, List[Tuple[float, float]]]
        for edge_begin, edge_ends in graph.edges_iter():
            for edge_end in edge_ends.keys():
                begin_node = graph.get_node(edge_begin)
                end_node = graph.get_node(edge_end)
                if begin_node and end_node:
                    edge_data["xs"].append((begin_node.x,
                                            end_node.x))
                    edge_data["ys"].append((begin_node.y,
                                            end_node.y))
        edge_data = ColumnDataSource(edge_data)
        # Get a figure
        figure = self.get_figure(height=600, width=1800, active_scroll="wheel_zoom")
        # figure.add_tools(HoverTool(tooltips=[("Type", "@type"), ("Path", "@name")]))
        lines = MultiLine(xs="xs", ys="ys", line_color="#8b8a8c")
        rectangles = Rect(x="center_x", y="center_y", width="width", height="height",
                          line_color="#8b8a8c", fill_color="color")
        text = Text(x="center_x", y="center_y", text="label", text_font_size="font_size",
                    text_baseline="middle", text_align="center")
        text_zoom_callback = CustomJS(args=dict(source=node_data,
                                                base_size=base_font_size),
                                      code="""
            var length = source.data.font_size.length;
            var start = this.start;
            var end = this.end;
            var factor = 7 / (this.end - this.start);
            for(var i = 0; i < length; i++) {
                let font_string_length = source.data.font_size[i].length;
                let font_size = base_size * factor;
                // source.data.font_size[i] = font_size + "pt";
                source.data.font_size[i] = "100%";
            }
            source.change.emit();
        """)
        figure.x_range = Range1d(-5, 5, min_interval=10)
        figure.y_range = Range1d(-5, 5, min_interval=10)
        figure.x_range.callback = text_zoom_callback
        # Plot the lines connecting the nodes
        figure.add_glyph(edge_data, lines)
        # Plot the nodes on the figure
        figure.add_glyph(node_data, rectangles)
        figure.add_glyph(node_data, text)
        # Render the graph
        self.render_graph(figure, self.output_dir, "structure_graph")
