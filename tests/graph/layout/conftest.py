import pytest
from depender.graph import StructureGraph


@pytest.fixture
def graph() -> StructureGraph:
    r"""Create a Graph objects that represents the following graph:

                          +-----+
                          |  1  |
                          |     |
                          +--+--+
                             |
           +-----------+-----+-----+-----------+
           |           |           |           |
        +--+--+     +--+--+     +--+--+     +--+--+
        |  2  |     |  3  |     |  4  |     |  5  |
        |     |     |     |     |     |     |     |
        +--+--+     +-----+     +--+--+     +-----+
           |                       |
           |                 +-----+-----+
           |                 |           |
        +--+--+           +--+--+     +--+--+
        |  6  |           |  7  |     |  8  |
        |     |           |     |     |     |
        +-----+           +-----+     +-----+

    Returns:
        Graph object
    """
    graph = StructureGraph()
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("1", "4")
    graph.add_edge("1", "5")
    graph.add_edge("2", "6")
    graph.add_edge("4", "7")
    graph.add_edge("4", "8")
    return graph


@pytest.fixture
def graph_with_labels() -> StructureGraph:
    r"""Create a Graph objects that represents the same graph as the previous fixture
    but with labels of different sizes

    Returns:
        Graph object
    """
    graph = StructureGraph()
    # Create the nodes first in order to set their labels
    graph.add_node("1", label="one")
    graph.add_node("2", label="two")
    graph.add_node("3", label="three")
    graph.add_node("4", label="four")
    graph.add_node("5", label="five")
    graph.add_node("6", label="six")
    graph.add_node("7", label="seven")
    graph.add_node("8", label="eight")
    # Then connect them using edges
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("1", "4")
    graph.add_edge("1", "5")
    graph.add_edge("2", "6")
    graph.add_edge("4", "7")
    graph.add_edge("4", "8")
    return graph
