import pytest
from depender.graph.graph import Graph
import hypothesis.strategies as st
from hypothesis import given


@given(name1=st.text(), name2=st.text())
def test_adding_and_removing_node(name1: str, name2: str):
    graph = Graph()
    assert not graph.nodes
    assert graph.node_count() == 0
    with pytest.raises(AttributeError):
        graph.get_node(name1)
    # Adding a single node and then removing it
    graph.add_node(name=name1)
    assert graph.nodes
    assert graph.node_exists(name1)
    assert graph.node_count() == 1
    graph.remove_node(name=name1)
    assert graph.node_count() == 0
    assert not graph.nodes
    # Adding a node with the same name a second time but different attributes
    # should overwrite the first one
    graph.add_node(name=name1, label=name1)
    graph.add_node(name=name1, label=name2)
    assert graph.nodes[name1].label == name2
    assert graph.node_count() == 1
    graph.remove_node(name=name1)
    # Removing a non-existent node should not raise an error
    graph.remove_node(name=name2)
    # Adding two nodes and then counting them
    if name2 == name1:
        name2 += "2"
    graph.add_node(name=name1)
    graph.add_node(name=name2)
    assert graph.node_count() == 2
    assert [name1, name2] == graph.get_all_node_names()


@given(source=st.text(), sink=st.text())
def test_adding_and_removing_edge(source: str, sink: str):
    graph = Graph()
    assert not graph.nodes
    assert not graph.edges
    # Adding a single edge and then removing it
    graph.add_edge(source=source, sink=sink)
    assert graph.node_exists(name=source)
    assert graph.node_exists(name=sink)
    assert graph.edge_exists(source=source, sink=sink)
    graph.remove_edge(source=source, sink=sink)
    assert not graph.edge_exists(source=source, sink=sink)
    # Adding an edge twice but different attributes
    # which should overwrite the first one
    graph.add_edge(source=source, sink=sink, color="blue")
    graph.add_edge(source=source, sink=sink, color="red")
    assert graph.edge_exists(source=source, sink=sink)
    edge = graph.get_edge(source=source, sink=sink)
    assert edge["color"] == "red"


def test_degree_computation():
    graph = Graph()
    graph.add_edge("node1", "node2")
    graph.add_edge("node2", "node1")
    graph.add_edge("node1", "node3")
    graph.add_edge("node1", "node4")
    graph.add_edge("node3", "node4")
    assert graph.in_degree("node1") == 1
    assert graph.out_degree("node1") == 3
    assert graph.in_degree("node2") == 1
    assert graph.out_degree("node2") == 1
    assert graph.in_degree("node3") == 1
    assert graph.out_degree("node3") == 1
    assert graph.in_degree("node4") == 2
    assert graph.out_degree("node4") == 0
