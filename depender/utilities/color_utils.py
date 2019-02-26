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
