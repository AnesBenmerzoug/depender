import os
from depender.graph.graph import StructureGraph
from depender.utilities.parsing import traverse_directory

from typing import List


class StructureParser:
    def __init__(self) -> None:
        self.graph = StructureGraph()

    def parse_project(self, directory: str,
                      excluded_directories: List[str],
                      follow_links: bool = True, depth: int = 5) -> StructureGraph:
        # Remove / if it is at the end of the given directory path
        if directory.endswith(os.path.sep):
            directory = directory[:-1]
        directory = os.path.abspath(directory)
        for root, dirs, files in traverse_directory(directory,
                                                    excluded_directories,
                                                    depth=depth, followlinks=follow_links):
            if not self.graph.node_exists(root):
                self.graph.add_node(root, label=os.path.basename(root), type="root")

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
