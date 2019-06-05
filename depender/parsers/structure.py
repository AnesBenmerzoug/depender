from pathlib import Path
from depender.graph.graph import StructureGraph
from depender.utilities.parsing import traverse_directory
from typing import List, Union


class StructureParser:
    def __init__(self) -> None:
        self.graph = StructureGraph()

    def parse_project(self, package_path: Union[str, Path],
                      excluded_directories: List[Union[str, Path]],
                      follow_links: bool = True, depth: int = 5) -> StructureGraph:
        if isinstance(package_path, str):
            package_path = Path(package_path)
        # Convert the excluded dirs to Path instances
        excluded_directories = list(map(lambda x: package_path.joinpath(x).resolve(),
                                        excluded_directories))
        for root, dirs, files in traverse_directory(package_path,
                                                    excluded_directories,
                                                    depth=depth, followlinks=follow_links):

            if not self.graph.node_exists(str(root)):
                self.graph.add_node(str(root), label=root.name, type="root")

            for i, element in enumerate(dirs + files):
                if "__pycache__" == element.name:
                    continue
                if ".pyc" == element.suffix:
                    continue

                # Add the actual node to the graph
                full_path = root / element

                if full_path.is_file():
                    self.graph.add_node(str(full_path), label=full_path.name, type="file")
                else:
                    self.graph.add_node(str(full_path), label=full_path.name, type="directory")

                # Connect the current root to the current file/directory
                self.graph.add_edge(str(root), str(full_path))
        return self.graph
