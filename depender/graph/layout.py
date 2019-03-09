from depender.graph.graph import Graph, Node
from typing import Union


def layout_structure_graph(graph: Graph, step_x: Union[int, float] = 1, step_y: Union[int, float] = 1.0) -> None:
    r"""
    Layout the structure graph using Buchheim's algorithm.

    Args:
        graph: Graph object that represents the structure graph
        step_x: Horizontal step size
        step_y: Vertical step size

    """
    root_node = graph.get_node(next(iter(graph.edges.keys())))

    first_walk(root_node, distance=step_x)
    second_walk(root_node, -root_node.x, distance=step_y)


def first_walk(current_node: Node, distance: Union[int, float] = 1.0) -> None:
    r"""
    First part of Buchheim's algorithm.
    The tree is traversed in a bottom up manner.

    Args:
        current_node: Current node object
        distance: Horizontal distance between sibling nodes.

    """
    # Get the current node's children and count them
    children = current_node.children
    children_count = len(children)
    if children_count == 0:
        if current_node.leftmost_sibling:
            current_node.x = current_node.left_sibling.x + distance
        else:
            current_node.x = 0
    else:
        # Make the default ancestor the leftmost child of the current node
        default_ancestor = children[0]
        for child in children:
            first_walk(child, distance)
            default_ancestor = apportion(child, default_ancestor, distance)

        execute_shifts(current_node)

        midpoint = (children[0].x + children[-1].x) / 2

        left_sibling = current_node.left_sibling
        if left_sibling:
            current_node.x = left_sibling.x + distance
            current_node.modifier = current_node.x - midpoint
        else:
            current_node.x = midpoint


def second_walk(current_node: Node, modifier: Union[int, float] = 0, depth: int = 0, distance: Union[int, float] = 1):
    r"""
    Second part of Buchheim's algorithm.
    The tree is traversed in a top down manner.

    Args:
        current_node: Current node object
        modifier: Distance by which the x position of the current node will be shifted
        depth: Depth of the current node in the graph
        distance: Vertical distance between levels in the graph

    """
    # Shift the current node's x position by modifier
    current_node.x += modifier
    # The current node's y position is equal to the current depth
    current_node.y = -depth * distance
    # Traverse the children of the current node
    for child in current_node.children:
        second_walk(child, modifier + current_node.modifier, depth + 1, distance)


def apportion(node: Node, default_ancestor: Node, distance: Union[int, float] = 1) -> Node:
    left_sibling = node.left_sibling
    if left_sibling is not None:
        v_inner_right = v_outer_right = node
        v_inner_left = left_sibling
        v_outer_left = v_inner_right.leftmost_sibling
        sir = v_inner_right.modifier
        sor = v_outer_right.modifier
        sil = v_inner_left.modifier
        sol = v_outer_left.modifier
        # Traverse the contours
        while next_right(v_inner_left) and next_left(v_inner_right):
            v_inner_left = next_right(v_inner_left)
            v_inner_right = next_left(v_inner_right)
            v_outer_left = next_left(v_outer_left)
            v_outer_right = next_right(v_outer_right)
            v_outer_right.ancestor = node
            shift = (v_inner_left.x + sil) - (v_inner_right.x + sir) + distance
            if shift > 0:
                a = ancestor(v_inner_left, node, default_ancestor)
                move_subtree(a, node, shift)
                sir = sir + shift
                sor = sor + shift
            sil += v_inner_left.modifier
            sir += v_inner_right.modifier
            sol += v_outer_left.modifier
            sor += v_outer_right.modifier
        if next_right(v_inner_left) and not next_right(v_outer_right):
            v_outer_right.thread = next_right(v_inner_left)
            v_outer_right.modifier += sil - sor
        elif next_left(v_inner_right) and not next_left(v_outer_left):
            v_outer_left.thread = next_left(v_inner_right)
            v_outer_left.modifier += sir - sol
        default_ancestor = node
    return default_ancestor


def next_left(node: Node) -> Node:
    r"""
    Traverse the left contour of the subtree rooted at node

    Args:
        node: Node from which the next node in the left contour will be taken

    Returns:
        Next node in the left contour

    """
    if node.children:
        return node.children[0]
    else:
        return node.thread


def next_right(node: Node) -> Node:
    r"""
    Traverse the right contour of the subtree rooted at node

    Args:
        node: Node from which the next node in the right contour will be taken

    Returns:
        Next node in the right contour

    """
    if node.children:
        return node.children[-1]
    else:
        return node.thread


def move_subtree(wl: Node, wr: Node, shift: Union[int, float]) -> None:
    subtrees = wr.index - wl.index
    wr.change -= shift / subtrees
    wr.shift += shift
    wl.change += shift / subtrees
    wr.x += shift
    wr.modifier += shift


def execute_shifts(node: Node) -> None:
    shift = change = 0
    for child in list(reversed(node.children)):
        child.x += shift
        child.modifier += shift
        change += child.change
        shift += child.shift + change


def ancestor(node_1: Node, node_2: Node, default_ancestor: Node) -> Node:
    r"""
    Get the greatest uncommon ancestor between node_1 and node_2 if found, otherwise return the default ancestor

    Args:
        node_1: First node
        node_2: Second node
        default_ancestor: Default ancestor to return in case an ancestor is not found

    Returns:
        Greatest uncommon ancestor or default ancestor
        
    """
    if node_1.ancestor in node_2.parent.children:
        return node_1.ancestor
    else:
        return default_ancestor


