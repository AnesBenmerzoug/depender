import os
from depender.utilities.graph import Graph

from typing import List


class StructureParser:
    def __init__(self) -> None:
        self.graph = Graph()

    def parse_project(self, directory: str,
                      excluded_directories: List[str],
                      follow_links: bool = True, depth: int = 5) -> Graph:
        # Remove / if it is at the end of the given directory path
        if directory.endswith(os.path.sep):
            directory = directory[:-1]
        directory = os.path.abspath(directory)
        root_directory = os.path.dirname(directory)
        root_depth = directory.count(os.path.sep)
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

            current_depth = root.count(os.path.sep) - root_depth

            # Don't go deeper than "depth" if it has a non-negative value
            if current_depth > depth >= 0:
                break

            if not self.graph.node_exists(root):
                self.graph.add_node(name=root, label=os.path.basename(root),
                                    type="root", depth=current_depth)
                self.graph.set_node_property(root, "children_count", 0)

            previous_point = None

            for i, element in enumerate(dirs + files):
                if "__pycache__" in element:
                    continue
                if ".pyc" in element:
                    continue

                # Add the actual node to the graph
                full_path = os.path.join(root, element)

                if os.path.isfile(full_path):
                    self.graph.add_node(full_path, label=os.path.basename(full_path),
                                        type="file", depth=current_depth + 1,
                                        children_count=0)
                else:
                    self.graph.add_node(full_path, label=os.path.basename(full_path),
                                        type="directory", depth=current_depth + 1,
                                        children_count=0)

                # Add an intermediate point to the graph to help with the plotting
                current_point = root[len(root_directory):] + "--point--" + full_path[len(root_directory):]
                self.graph.add_node(current_point, label="",
                                    type="point", color=None, depth=current_depth + 0.5)

                # Connect the current root to the current file/directory through the point(s)
                if previous_point is None:
                    self.graph.add_edge(root, current_point)
                    self.graph.add_edge(current_point, full_path)
                else:
                    self.graph.add_edge(previous_point, current_point)
                    self.graph.add_edge(current_point, full_path)
                self.graph.set_node_property(root, "children_count",
                                             self.graph.get_node_property(root, "children_count") + 1)
                previous_point = current_point

        return self.graph
