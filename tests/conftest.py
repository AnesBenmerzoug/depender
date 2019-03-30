import pytest
from depender.graph.graph import Graph


@pytest.fixture
def graph() -> Graph:
    r"""
    Create a Graph objects that represents the following graph:

                          +-----+
                          |  1  |
                          |     |
                          +--+--+
                             |
           +-----------------------+-----------+
           |           |           |           |
        +--+--+     +--+--+     +--+--+     +--+--+
        |  2  |     |  3  |     |  4  |     |  5  |
        |     |     |     |     |     |     |     |
        +--+--+     +-----+     +--+--+     +-----+
           |                       |
           |           +-----------+
           |           |           |
        +--+--+     +--+--+     +--+--+
        |  6  |     |  7  |     |  8  |
        |     |     |     |     |     |
        +-----+     +-----+     +-----+

    Returns:

    """
    graph = Graph()
    graph.add_edge("1", "2")
    graph.add_edge("1", "3")
    graph.add_edge("1", "4")
    graph.add_edge("1", "5")
    graph.add_edge("2", "6")
    graph.add_edge("4", "7")
    graph.add_edge("4", "8")
    return graph
