from depender.graph.layout import layout_structure_graph
import pytest


def test_structure_layout(graph) -> None:
    layout_structure_graph(graph, base_distance_x=1, base_distance_y=1)
    assert graph.get_node("1").x == 0.0
    assert graph.get_node("2").x == -3.0
    assert graph.get_node("3").x == -1.0
    assert graph.get_node("4").x == 1.0
    assert graph.get_node("5").x == 3.0
    assert graph.get_node("6").x == -3.0
    assert graph.get_node("7").x == 0.0
    assert graph.get_node("8").x == 2.0
