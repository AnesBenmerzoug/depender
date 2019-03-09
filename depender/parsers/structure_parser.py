import os
from depender.graph.graph import Graph

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
                self.graph.add_node(name=root, label=os.path.basename(root), type="root")

            for i, element in enumerate(dirs + files):
                if "__pycache__" in element:
                    continue
                if ".pyc" in element:
                    continue

                # Add the actual node to the graph
                full_path = os.path.join(root, element)

                if os.path.isfile(full_path):
                    self.graph.add_node(full_path, label=os.path.basename(full_path), type="file")
                else:
                    self.graph.add_node(full_path, label=os.path.basename(full_path), type="directory")

                # Connect the current root to the current file/directory
                self.graph.add_edge(root, full_path)

        return self.graph
