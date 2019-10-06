import hypothesis.strategies as st
import pytest
from depender.graph.node import Node
from hypothesis import given


@given(name=st.text())
def test_node_default_initialization(name: str):
    node = Node(name=name)
    assert node.name == name
    assert node.label == ""
    assert node.type is None
    assert node.x == 0
    assert node.y == 0
    assert node.width == 0
    assert node.height == 0
    assert node.index == 1
    assert node.change == 0
    assert node.shift == 0
    assert node.modifier == 0
    assert node.thread is None
    assert node.parent is None
    assert node.children == list()
    assert node.ancestor is node
    assert node.leftmost_sibling is None
    assert node.left_sibling is None


@given(label=st.text())
def test_node_setting_and_getting_attributes_like_a_dict(label: str):
    node = Node(name="test")
    node["label"] = label
    assert node.label == label
    assert node["label"] == label
    with pytest.raises(AttributeError):
        node["cake"] = "we ain't got no cake"
    with pytest.raises(AttributeError):
        cake = node["cake"]
