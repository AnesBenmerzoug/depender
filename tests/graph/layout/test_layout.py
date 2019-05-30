from depender.graph.layout import layout_structure_graph
from depender.graph import StructureGraph


def test_structure_layout(graph: StructureGraph) -> None:
    layout_structure_graph(graph, base_distance_x=1, base_distance_y=1)
    # Check X coordinates
    assert graph.get_node("1").x == 0.0
    assert graph.get_node("2").x == -1.5
    assert graph.get_node("3").x == -0.5
    assert graph.get_node("4").x == 0.5
    assert graph.get_node("5").x == 1.5
    assert graph.get_node("6").x == -1.5
    assert graph.get_node("7").x == 0.0
    assert graph.get_node("8").x == 1.0
    # Check Y coordinates
    assert graph.get_node("1").y == 0.0
    assert graph.get_node("2").y == -1.0
    assert graph.get_node("3").y == -1.0
    assert graph.get_node("4").y == -1.0
    assert graph.get_node("5").y == -1.0
    assert graph.get_node("6").y == -2.0
    assert graph.get_node("7").y == -2.0
    assert graph.get_node("8").y == -2.0


def test_structure_layout_with_label(graph_with_labels: StructureGraph) -> None:
    graph = graph_with_labels
    layout_structure_graph(graph, base_distance_x=1, base_distance_y=1)
    # Check X coordinates
    assert graph.get_node("1").x == 0.0
    assert graph.get_node("2").x == -7.75
    assert graph.get_node("3").x == -2.75
    assert graph.get_node("4").x == 2.75
    assert graph.get_node("5").x == 7.75
    assert graph.get_node("6").x == -7.75
    assert graph.get_node("7").x == -0.25
    assert graph.get_node("8").x == 5.75
    # Check Y coordinates
    assert graph.get_node("1").y == 0.0
    assert graph.get_node("2").y == -1.0
    assert graph.get_node("3").y == -1.0
    assert graph.get_node("4").y == -1.0
    assert graph.get_node("5").y == -1.0
    assert graph.get_node("6").y == -2.0
    assert graph.get_node("7").y == -2.0
    assert graph.get_node("8").y == -2.0
