from depender.graph.node import Node
from depender.graph.graph import StructureGraph
from typing import Optional


def layout_structure_graph(graph: StructureGraph,
                           base_distance_x: float = 1.0,
                           base_distance_y: float = 1.0) -> None:
    r"""Layout the structure graph using a modified version of Buchheim's algorithm
    that takes into account the width and height of the nodes which are proportional 
    to the length of the nodes' labels and to the font size

    Args:
        graph: Graph object that represents the structure graph
        base_distance_x: Base horizontal step size which when multiplied by the node's label length
            gives the actual horizontal step size.
        base_distance_y: Base vertical step size which is used to determine a node's height 
            and the distance between levels in the graph
    """
    root_node = graph.get_root_node()
    if root_node is not None:
        first_walk(root_node, base_distance=base_distance_x)
        second_walk(root_node, -root_node.x, base_distance=base_distance_y)


def first_walk(current_node: Node, base_distance: float = 1.0) -> None:
    r"""First part of Buchheim's algorithm.
    The tree is traversed in a bottom up manner.

    Args:
        current_node: Current node object
        base_distance: Base horizontal distance between sibling nodes.
            it will be multiplied by factor proportional to the node's label in order
            to obtain the actual distance
    """
    # Get the current node's children and count them
    children = current_node.children
    children_count = len(children)
    if children_count == 0:
        if current_node.left_sibling:
            current_node.x = current_node.left_sibling.x \
                + (current_node.left_sibling.width + current_node.width) / 2 \
                + base_distance
        else:
            current_node.x = 0
    else:
        # Make the default ancestor the leftmost child of the current node
        default_ancestor = children[0]
        for child in children:
            first_walk(child, base_distance)
            default_ancestor = apportion(child, default_ancestor, base_distance)

        execute_shifts(current_node)
        # Compute the current node's children's center point's x coordinate
        if len(children) % 2 == 0:
            midpoint = (children[0].x + children[-1].x) / 2
        else:
            midpoint = children[len(children) // 2].x
        # If the current node has no left sibling i.e. is the leftmost one
        # then assign the midpoint coordinate to it, else shift from its left sibling
        # and compute the modifier value
        if current_node.left_sibling:
            current_node.x = current_node.left_sibling.x \
                    + (current_node.left_sibling.width + current_node.width) / 2 \
                    + base_distance
            current_node.modifier = current_node.x - midpoint
        else:
            current_node.x = midpoint


def second_walk(current_node: Node, 
                modifier: float = 0, 
                depth: int = 0, 
                base_distance: float = 1):
    r"""Second part of Buchheim's algorithm.
    The tree is traversed in a top down manner.

    Args:
        current_node: Current node object
        modifier: Distance by which the x position of the current node will be shifted
        depth: Depth of the current node in the graph
        base_distance: Vertical distance between levels in the graph
    """
    # Shift the current node's x position by an amount equal to modifier
    # and increment modifier by an amount equal to the current node's modifier property
    current_node.x += modifier
    modifier += current_node.modifier
    # The current node's y position is equal to the current depth times 1 + the height
    current_node.y = -depth * (current_node.height + base_distance)
    for child in current_node.children:
        second_walk(child, modifier, depth + 1, base_distance)


def apportion(current_node: Node, default_ancestor: Node, base_distance: float) -> Node:
    r"""
    
    Args:
        current_node: 
        default_ancestor: 
        base_distance: Base horizontal distance between sibling nodes

    Returns:
        Either the given default ancestor node or the current node
    """
    left_sibling = current_node.left_sibling
    leftmost_sibling = current_node.leftmost_sibling
    if left_sibling is not None and leftmost_sibling is not None:
        v_inner_right = v_outer_right = current_node
        v_inner_left = left_sibling
        v_outer_left = leftmost_sibling
        sir = v_inner_right.modifier
        sor = v_outer_right.modifier
        sil = v_inner_left.modifier
        sol = v_outer_left.modifier
        # Traverse the contours
        next_inner_left = next_right(v_inner_left)
        next_inner_right = next_left(v_inner_right)
        next_outer_left = next_left(v_outer_left)
        next_outer_right = next_right(v_outer_right)
        while next_inner_left and next_inner_right and next_outer_right and next_outer_left:
            v_inner_left = next_inner_left
            v_inner_right = next_inner_right
            v_outer_left = next_outer_left
            v_outer_right = next_outer_right
            v_outer_right.ancestor = current_node
            # shift = (v_inner_left.x + sil) - (v_inner_right.x + sir)
            shift = (v_inner_left.x + sil) - (v_inner_right.x + sir) \
                + (v_inner_left.width + v_inner_right.width) / 2 \
                + base_distance
            if shift > 0:
                a = ancestor(v_inner_left, current_node, default_ancestor)
                move_subtree(a, current_node, shift)
                sir = sir + shift
                sor = sor + shift
            sil += v_inner_left.modifier
            sir += v_inner_right.modifier
            sol += v_outer_left.modifier
            sor += v_outer_right.modifier
            # Get the next elements in the contours
            next_inner_left = next_right(v_inner_left)
            next_inner_right = next_left(v_inner_right)
            next_outer_left = next_left(v_outer_left)
            next_outer_right = next_right(v_outer_right)
        if next_right(v_inner_left) and not next_right(v_outer_right):
            v_outer_right.thread = next_right(v_inner_left)
            v_outer_right.modifier += sil - sor
        if next_left(v_inner_right) and not next_left(v_outer_left):
            v_outer_left.thread = next_left(v_inner_right)
            v_outer_left.modifier += sir - sol
        default_ancestor = current_node
    return default_ancestor


def move_subtree(left_ancestor: Node, right_ancestor: Node, shift: float) -> None:
    r"""Shift the right subtree rooted at the right ancestor

    Args:
        left_ancestor: Ancestor node of the left subtree
        right_ancestor: Ancestor node of the right subtree
        shift: Amount by which the right subtree will be shifted
    """
    num_subtrees_between_ancestors = right_ancestor.index - left_ancestor.index
    right_ancestor.change -= shift / num_subtrees_between_ancestors
    right_ancestor.shift += shift
    left_ancestor.change += shift / num_subtrees_between_ancestors
    right_ancestor.x += shift
    right_ancestor.modifier += shift


def execute_shifts(node: Node) -> None:
    shift = change = 0  # type: float
    for child in list(reversed(node.children)):
        child.x += shift
        child.modifier += shift
        change += child.change
        shift += child.shift + change


def next_left(node: Node) -> Optional[Node]:
    r"""Traverse the left contour of the subtree rooted at node

    Args:
        node: Node from which the next node in the left contour will be taken

    Returns:
        Next node in the left contour
    """
    if node.children:
        return node.children[0]
    else:
        return node.thread


def next_right(node: Node) -> Optional[Node]:
    r"""Traverse the right contour of the subtree rooted at node

    Args:
        node: Node from which the next node in the right contour will be taken

    Returns:
        Next node in the right contour
    """
    if node.children:
        return node.children[-1]
    else:
        return node.thread


def ancestor(node_1: Node, node_2: Node, default_ancestor: Node) -> Node:
    r"""Get the left greatest uncommon ancestor between node_1 and node_2 if found,
    otherwise return the default ancestor

    Args:
        node_1: First node
        node_2: Second node
        default_ancestor: Default ancestor to return in case an ancestor is not found

    Returns:
        Greatest uncommon ancestor or default ancestor
    """
    if node_1.ancestor and node_2.parent:
        if node_1.ancestor in node_2.parent.children:
            return node_1.ancestor
    return default_ancestor


