from depender.graph.structure import StructureGraph


def test_structure_layout(graph: StructureGraph) -> None:
    graph.layout(base_distance_x=1, base_distance_y=1)
    # Check X coordinates
    assert graph.nodes["1"]["x"] == 0.0
    assert graph.nodes["2"]["x"] == -1.5
    assert graph.nodes["3"]["x"] == -0.5
    assert graph.nodes["4"]["x"] == 0.5
    assert graph.nodes["5"]["x"] == 1.5
    assert graph.nodes["6"]["x"] == -1.5
    assert graph.nodes["7"]["x"] == 0.0
    assert graph.nodes["8"]["x"] == 1.0
    # Check Y coordinates
    assert graph.nodes["1"]["y"] == 0.0
    assert graph.nodes["2"]["y"] == -1.0
    assert graph.nodes["3"]["y"] == -1.0
    assert graph.nodes["4"]["y"] == -1.0
    assert graph.nodes["5"]["y"] == -1.0
    assert graph.nodes["6"]["y"] == -2.0
    assert graph.nodes["7"]["y"] == -2.0
    assert graph.nodes["8"]["y"] == -2.0


def test_structure_layout_with_label(graph_with_labels: StructureGraph) -> None:
    graph_with_labels.layout(base_distance_x=1, base_distance_y=1)
    # Check X coordinates
    assert graph_with_labels.nodes["1"]["x"] == 0.0
    assert graph_with_labels.nodes["2"]["x"] == -7.75
    assert graph_with_labels.nodes["3"]["x"] == -2.75
    assert graph_with_labels.nodes["4"]["x"] == 2.75
    assert graph_with_labels.nodes["5"]["x"] == 7.75
    assert graph_with_labels.nodes["6"]["x"] == -7.75
    assert graph_with_labels.nodes["7"]["x"] == -0.25
    assert graph_with_labels.nodes["8"]["x"] == 5.75
    # Check Y coordinates
    assert graph_with_labels.nodes["1"]["y"] == 0.0
    assert graph_with_labels.nodes["2"]["y"] == -1.0
    assert graph_with_labels.nodes["3"]["y"] == -1.0
    assert graph_with_labels.nodes["4"]["y"] == -1.0
    assert graph_with_labels.nodes["5"]["y"] == -1.0
    assert graph_with_labels.nodes["6"]["y"] == -2.0
    assert graph_with_labels.nodes["7"]["y"] == -2.0
    assert graph_with_labels.nodes["8"]["y"] == -2.0
