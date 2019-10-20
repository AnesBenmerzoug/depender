from typing import List

from loguru import logger
from networkx import DiGraph

__all__ = ["StructureGraph"]


class StructureGraph(DiGraph):
    def children(self, node: str) -> List[str]:
        return list(self.successors(node))

    def add_node(self, node_for_adding, **attr):
        super().add_node(node_for_adding, **attr)
        # Initial properties that are needed for the structure graph
        self.nodes[node_for_adding]["children"] = []
        self.nodes[node_for_adding]["parent"] = None
        self.nodes[node_for_adding]["ancestor"] = None
        self.nodes[node_for_adding]["leftmost_sibling"] = None
        self.nodes[node_for_adding]["left_sibling"] = None
        self.nodes[node_for_adding]["thread"] = None
        self.nodes[node_for_adding]["x"] = 0
        self.nodes[node_for_adding]["y"] = 0
        self.nodes[node_for_adding]["width"] = 0
        self.nodes[node_for_adding]["height"] = 0
        self.nodes[node_for_adding]["index"] = 0
        self.nodes[node_for_adding]["shift"] = 0
        self.nodes[node_for_adding]["modifier"] = 0
        self.nodes[node_for_adding]["change"] = 0

    def add_edge(self, source: str, sink: str, **kwargs):
        super().add_edge(source, sink, **kwargs)
        # Add properties to both nodes
        self.nodes[source]["children"] += [sink]
        self.nodes[sink]["parent"] = source
        self.nodes[sink]["ancestor"] = sink
        self.nodes[sink]["index"] = len(list(self.successors(source)))
        # Add siblings
        if len(list(self.successors(source))) > 1:
            self.nodes[sink]["leftmost_sibling"] = next(iter(self.successors(source)))
            self.nodes[sink]["left_sibling"] = list(self.successors(source))[-2]

    @property
    def root_node(self) -> str:
        if not self.nodes:
            raise AttributeError("This graph is empty")
        return next(iter(self.nodes))

    def layout(self, **kwargs):
        base_distance_x = kwargs.pop("base_distance_x", 1.0)
        base_distance_y = kwargs.pop("base_distance_y", 1.0)
        root_node = self.root_node
        if root_node is not None:
            with logger.catch(reraise=True):
                self._first_walk(root_node, base_distance=base_distance_x)
                self._second_walk(
                    root_node,
                    -self.nodes[root_node]["x"],
                    base_distance=base_distance_y,
                )

    def _first_walk(self, current_node: str, base_distance: float = 1.0):
        # Get the current node's children and count them
        children = self.nodes[current_node]["children"]
        children_count = len(children)
        if children_count == 0:
            left_sibling = self.nodes[current_node].get("left_sibling", None)
            if left_sibling:
                self.nodes[current_node]["x"] = (
                    self.nodes[left_sibling]["x"]
                    + (
                        self.nodes[left_sibling]["width"]
                        + self.nodes[current_node]["width"]
                    )
                    / 2
                    + base_distance
                )
            else:
                self.nodes[current_node]["x"] = 0
        else:
            # Make the default ancestor the leftmost child of the current node
            default_ancestor = children[0]
            print(children)
            for child in children:
                self._first_walk(child, base_distance)
                default_ancestor = self._apportion(
                    child, default_ancestor, base_distance
                )

            self._execute_shifts(current_node)
            # Compute the current node's children's center point's x coordinate
            if len(children) % 2 == 0:
                midpoint = (
                    self.nodes[children[0]]["x"] + self.nodes[children[-1]]["x"]
                ) / 2
            else:
                midpoint = self.nodes[children[len(children) // 2]]["x"]
            # If the current node has no left sibling i.e. is the leftmost one
            # then assign the midpoint coordinate to it, else shift from its left sibling
            # and compute the modifier value
            left_sibling = self.nodes[current_node].get("left_sibling", None)
            if left_sibling:
                self.nodes[current_node]["x"] = (
                    self.nodes[left_sibling]["x"]
                    + (
                        self.nodes[left_sibling]["width"]
                        + self.nodes[current_node]["width"]
                    )
                    / 2
                    + base_distance
                )
                self.nodes[current_node]["modifier"] = (
                    self.nodes[current_node]["x"] - midpoint
                )
            else:
                self.nodes[current_node]["x"] = midpoint

    def _second_walk(
        self,
        current_node,
        modifier: float = 0,
        depth: int = 0,
        base_distance: float = 1,
    ):
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
        self.nodes[current_node]["x"] += modifier
        modifier += self.nodes[current_node]["modifier"]
        # The current node's y position is equal to the current depth times 1 + the height
        self.nodes[current_node]["y"] = -depth * (
            self.nodes[current_node]["height"] + base_distance
        )
        for child in self.nodes[current_node]["children"]:
            self._second_walk(child, modifier, depth + 1, base_distance)

    def _apportion(
        self, current_node: str, default_ancestor: str, base_distance: float
    ):
        r"""

        Args:
            current_node:
            default_ancestor:
            base_distance: Base horizontal distance between sibling nodes

        Returns:
            Either the given default ancestor node or the current node
        """
        left_sibling = self.nodes[current_node]["left_sibling"]
        leftmost_sibling = self.nodes[current_node]["leftmost_sibling"]
        if left_sibling is not None and leftmost_sibling is not None:
            v_inner_right = v_outer_right = current_node
            v_inner_left = left_sibling
            v_outer_left = leftmost_sibling
            sir = self.nodes[v_inner_right]["modifier"]
            sor = self.nodes[v_outer_right]["modifier"]
            sil = self.nodes[v_inner_left]["modifier"]
            sol = self.nodes[v_outer_left]["modifier"]
            # Traverse the contours
            next_inner_left = self._next_right(v_inner_left)
            next_inner_right = self._next_left(v_inner_right)
            next_outer_left = self._next_left(v_outer_left)
            next_outer_right = self._next_right(v_outer_right)
            while (
                next_inner_left
                and next_inner_right
                and next_outer_right
                and next_outer_left
            ):
                v_inner_left = next_inner_left
                v_inner_right = next_inner_right
                v_outer_left = next_outer_left
                v_outer_right = next_outer_right
                self.nodes[v_outer_right]["ancestor"] = current_node
                # shift = (v_inner_left.x + sil) - (v_inner_right.x + sir)
                shift = (
                    (self.nodes[v_inner_left]["x"] + sil)
                    - (self.nodes[v_inner_right]["x"] + sir)
                    + (
                        self.nodes[v_inner_left]["width"]
                        + self.nodes[v_inner_right]["width"]
                    )
                    / 2
                    + base_distance
                )
                if shift > 0:
                    a = self._ancestor(v_inner_left, current_node, default_ancestor)
                    self._move_subtree(a, current_node, shift)
                    sir = sir + shift
                    sor = sor + shift
                sil += self.nodes[v_inner_left]["modifier"]
                sir += self.nodes[v_inner_right]["modifier"]
                sol += self.nodes[v_outer_left]["modifier"]
                sor += self.nodes[v_outer_right]["modifier"]
                # Get the next elements in the contours
                next_inner_left = self._next_right(v_inner_left)
                next_inner_right = self._next_left(v_inner_right)
                next_outer_left = self._next_left(v_outer_left)
                next_outer_right = self._next_right(v_outer_right)
            if self._next_right(v_inner_left) and not self._next_right(v_outer_right):
                self.nodes[v_outer_right]["thread"] = self._next_right(v_inner_left)
                self.nodes[v_outer_right]["modifier"] += sil - sor
            if self._next_left(v_inner_right) and not self._next_left(v_outer_left):
                self.nodes[v_outer_left]["thread"] = self._next_left(v_inner_right)
                self.nodes[v_outer_left]["modifier"] += sir - sol
            default_ancestor = current_node
        return default_ancestor

    def _move_subtree(self, left_ancestor, right_ancestor, shift: float) -> None:
        r"""Shift the right subtree rooted at the right ancestor

        Args:
            left_ancestor: Ancestor node of the left subtree
            right_ancestor: Ancestor node of the right subtree
            shift: Amount by which the right subtree will be shifted
        """
        num_subtrees_between_ancestors = (
            self.nodes[right_ancestor]["index"] - self.nodes[left_ancestor]["index"]
        )
        self.nodes[right_ancestor]["change"] -= shift / num_subtrees_between_ancestors
        self.nodes[right_ancestor]["shift"] += shift
        self.nodes[left_ancestor]["change"] += shift / num_subtrees_between_ancestors
        self.nodes[right_ancestor]["x"] += shift
        self.nodes[right_ancestor]["modifier"] += shift

    def _execute_shifts(self, node):
        shift = change = 0  # type: float
        for child in list(reversed(self.nodes[node]["children"])):
            self.nodes[child]["x"] += shift
            self.nodes[child]["modifier"] += shift
            change += self.nodes[child]["change"]
            shift += self.nodes[child]["shift"] + change

    def _next_left(self, node):
        r"""Traverse the left contour of the subtree rooted at node

        Args:
            node from which the next node in the left contour will be taken

        Returns:
            Next node in the left contour
        """
        children = self.nodes[node]["children"]
        thread = self.nodes[node]["thread"]
        if children:
            return children[0]
        else:
            return thread

    def _next_right(self, node):
        r"""Traverse the right contour of the subtree rooted at node

        Args:
            node from which the next node in the right contour will be taken

        Returns:
            Next node in the right contour
        """
        children = self.nodes[node]["children"]
        thread = self.nodes[node]["thread"]
        if children:
            return children[-1]
        else:
            return thread

    def _ancestor(self, node_1, node_2, default_ancestor):
        r"""Get the left greatest uncommon ancestor between node_1 and node_2 if found,
        otherwise return the default ancestor

        Args:
            node_1: First node
            node_2: Second node
            default_ancestor: Default ancestor to return in case an ancestor is not found

        Returns:
            Greatest uncommon ancestor or default ancestor
        """
        node_1_ancestor = self.nodes[node_1]["ancestor"]
        node_2_parent = self.nodes[node_2]["parent"]
        if node_1_ancestor and node_2_parent:
            if node_1_ancestor in self.nodes[node_2_parent]["children"]:
                return node_1_ancestor
        return default_ancestor
