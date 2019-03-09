from depender.graph.graph import Graph, Node


def layout_structure_graph(graph: Graph) -> None:

    for source, sinks in graph.edges_iter():
        for sink in sinks.keys():
            print(f"source: {source} -> sink: {sink}")

    root_node = graph.get_node(next(iter(graph.edges.keys())))

    def first_walk(current_node: Node, distance: int = 1) -> None:
        r"""
        First part of Buchheim's algorithm.
        The tree is traversed in a bottom up manner.

        Args:
            current_node: Current node object
            distance: Distance between sibling nodes.

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
            default_ancestor = children[0]
            for child in children:
                first_walk(child, distance)
                default_ancestor = apportion(child, default_ancestor, distance)

            add_offsets(current_node)

            midpoint = (children[0].x + children[-1].x) / 2

            left_sibling = current_node.left_sibling
            if left_sibling:
                current_node.x = left_sibling.x + 1
                current_node.modifier = current_node.x - midpoint
            else:
                current_node.x = midpoint

    def apportion(node: Node, default_ancestor: Node, distance: int = 1):
        left_sibling = node.left_sibling
        if left_sibling is not None:
            v_inner_right = v_outer_right = node
            v_inner_left = left_sibling
            v_outer_left = node.leftmost_sibling
            sir = sor = node.modifier
            sil = v_inner_left.modifier
            sol = v_outer_left.modifier
            while v_inner_left.right_sibling and v_inner_right.left_sibling:
                v_inner_left = v_inner_left.right_sibling
                v_inner_right = v_inner_right.left_sibling
                v_outer_left = v_outer_left.left_sibling
                v_outer_right = v_outer_right.right_sibling
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
            if v_inner_left.right_sibling and not v_outer_right.right_sibling:
                v_outer_right.thread = v_inner_left.right_sibling
                v_outer_right.modifier +=  + sil - sor
            elif v_inner_right.left_sibling and not v_outer_left.left_sibling:
                v_outer_left.thread = v_inner_right.left_sibling
                v_outer_left.modifier += sir - sol
            default_ancestor = node
        return default_ancestor

    def move_subtree(wl: Node, wr: Node, shift: int):
        subtrees = wr.index - wl.index
        wr.change -= shift / subtrees
        wr.shift += shift
        wl.change += shift / subtrees
        wr.x += shift
        wr.modifier += shift

    def add_offsets(node: Node):
        shift = change = 0
        for child in list(reversed(node.children)):
            child.x += shift
            child.modifier += shift
            change += child.change
            shift += child.shift + change

    def ancestor(v_inner_left: Node, node: Node, default_ancestor: Node):
        if v_inner_left.ancestor in node.parent.children:
            return v_inner_left.ancestor
        else:
            return default_ancestor

    def second_walk(node: Node, modifier: int = 0, depth: int = 0):
        node.x += modifier
        # The current node's y position is equal to the current depth
        node.y = -depth

        for child in node.children:
            second_walk(child, modifier + node.modifier, depth + 1)

    first_walk(root_node)
    second_walk(root_node)

