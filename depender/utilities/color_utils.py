from typing import List, Optional


def hex_to_rgb(hex: str) -> List[int]:
    r"""
    #FFFFFF" -> [255,255,255]
    """
    # Pass 16 to the integer function for change of base
    return [int(hex[2*i+1:2*i+3], 16) for i in (0, 1, 2)]


def rgb_to_hex(rgb: List[int]) -> str:
    r"""
    [255,255,255] -> "#FFFFFF"
    """
    # Components need to be integers for hex to make sense
    rgb = [int(x) for x in rgb]
    return "#"+"".join(["0{0:x}".format(v) if v < 16 else
                        "{0:x}".format(v) for v in rgb])


def color_dict(gradient: List[List[int]]) -> dict:
    r"""
    Takes in a list of RGB sub-lists and returns dictionary of
    colors in RGB and hex form for use in a graphing function
    defined later on
    """
    return {"hex": [rgb_to_hex(rgb) for rgb in gradient],
            "r": [rgb[0] for rgb in gradient],
            "g": [rgb[1] for rgb in gradient],
            "b": [rgb[2] for rgb in gradient]}


def linear_gradient(source_color: str, sink_color: str, in_degree: int = 1, out_degree: int = 1) -> str:
    r"""
    Function that returns a color that is the weighted average of the source
    and sink colors depending on the given in and out degrees.
    """
    # Starting and ending colors in RGB form
    source = hex_to_rgb(source_color)
    sink = hex_to_rgb(sink_color)
    new_color = list()
    for i in range(3):
        new_color.append(int(max(min((in_degree * source[i] + out_degree * sink[i])/(in_degree + out_degree), 255), 0)))
    return rgb_to_hex(new_color)


"""
def prettify_graph(graph: Graph, source_color: Optional[str] = None, sink_color: Optional[str] = None,
                   not_connected_color: Optional[str] = None) -> None:
    if None in [source_color, sink_color, not_connected_color]:
        print("Can't colorize the graph with None")
    # Customizing the colors
    for node in graph.nodes_iter():
        label = node.attr.get("label")
        if " external" in label:
            label = label[:label.find(" external")]
            if "." in label:
                label = label[:label.rfind(".")] + "\n" + label[label.rfind("."):]
        else:
            if "." in label:
                label = label[:label.rfind(".")] + "\n" + label[label.rfind("."):] + ".py"
        node.attr.update(label=label)
        in_degree = graph.in_degree(node)
        out_degree = graph.out_degree(node)
        if in_degree == 0 and out_degree == 0:
            node.attr.update(style="filled")
            node.attr.update(fillcolor=not_connected_color)
        elif out_degree == 0:
            node.attr.update(style="filled")
            node.attr.update(fillcolor=linear_gradient(source_color, sink_color, in_degree, out_degree))
        elif in_degree == 0:
            node.attr.update(style="filled")
            node.attr.update(fillcolor=linear_gradient(source_color, sink_color, in_degree, out_degree))
        else:
            node.attr.update(style="filled")
            node.attr.update(fillcolor=linear_gradient(source_color, sink_color, in_degree, out_degree))
    for edge in graph.edges_iter():
        color_list = [graph.get_node(edge[0]).attr.get("fillcolor"), graph.get_node(edge[1]).attr.get("fillcolor")]
        while len(color_list) < 2:
            current_colors = color_list[:]
            for i in range(len(current_colors)-1):
                color_list.insert(i+1, linear_gradient(current_colors[i], current_colors[i+1]))
        gradient = list()
        for color in color_list:
            gradient.append("{color};{value}".format(color=color, value=1.0 / len(color_list)))
        edge.attr.update(color=":".join(gradient))
        # edge.attr.update(color=f"{color2};0.33:{color1};0.33")
"""
