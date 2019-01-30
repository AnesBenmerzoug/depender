import os
from depender.utilities.graph import Graph

from typing import List, Optional


class StructureParser:
    def __init__(self, root_dir_color: str, dir_color: str, file_color: str) -> None:
        self.graph = Graph(strict=True, splines="polyline", overlap=False,
                           node_shape="folder", node_style="filled",
                           rankdir="TB", directed=False)
        self.root_dir_color = root_dir_color
        self.dir_color = dir_color
        self.file_color = file_color

    def parse_project(self, directory: str,
                      excluded_directories: List[str],
                      follow_links: bool = True, depth: Optional[int] = None) -> Graph:
        # Remove / if it is at the end of the given directory path
        if directory.endswith(os.path.sep):
            directory = directory[:-1]
        if directory == ".":
            directory = os.path.abspath(directory)
        root_separator_count = directory.count(os.path.sep)
        for root, dirs, files in os.walk(directory, followlinks=follow_links):
            # Check to see if there are user specified directories that should be skipped
            skip = False
            if excluded_directories is not None:
                for folder_to_exclude in excluded_directories:
                    if os.path.sep + folder_to_exclude in root:
                        skip = True
                        break
            if skip is True:
                continue

            # Skip __pycache__ directories
            if "__pycache__" in root:
                continue

            # Skip hidden directories
            if "/." in root:
                continue

            # Don't go deeper than "depth" if it has a non-negative value
            if depth is not None and depth >= 0:
                current_separator_count = root.count(os.path.sep)
                if root_separator_count + depth < current_separator_count:
                    continue

            # Get the label for the current root node
            if os.path.sep in root:
                root_label = root.split(os.path.sep)[-1]
            else:
                root_label = root

            try:
                self.graph.get_node(name=root)
            except KeyError:
                self.graph.add_node(name=root, label=root_label, color=self.root_dir_color)

            point_after_root = root + "_dot"
            self.graph.add_node(point_after_root, shape="point", width="0", height="0")
            self.graph.add_edge(root, point_after_root, weight="1000")

            points = [point_after_root]
            next_elements = []
            previous_point = None

            for i, element in enumerate(dirs + files):
                if "__pycache__" in element:
                    continue
                if element.startswith("."):
                    continue
                if ".pyc" in element:
                    continue

                # Add the actual node to the graph
                full_path = os.path.join(root, element)
                next_elements.append(full_path)

                if os.path.isfile(full_path):
                    self.graph.add_node(full_path, label=element, shape="note", color=self.file_color)
                else:
                    self.graph.add_node(full_path, label=element, color=self.dir_color)

                if previous_point is None:
                    connecting_point = point_after_root
                else:
                    connecting_point = full_path + "_dot_2"
                    self.graph.add_node(connecting_point, shape="point", width="0", height="0")
                    points.append(connecting_point)

                previous_point = connecting_point

            # Add the connecting points to the graph and connect them together
            self.graph.add_subgraph(points, rank="same")
            for i in range(len(points)-1):
                self.graph.add_edge(points[i], points[i+1], weight="60")
            # Add the elements of the next level to the graph and connect each one of them
            # to the corresponding point
            self.graph.add_subgraph(next_elements, rank="same")
            for i in range(len(next_elements)):
                self.graph.add_edge(points[i], next_elements[i], weight="1000")

        return self.graph
