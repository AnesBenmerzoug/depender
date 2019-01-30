import os
import ast
import importlib
import importlib.util
from depender.utilities.graph import Graph
from depender.utilities.color_utils import prettify_graph
from collections import defaultdict
from difflib import SequenceMatcher

from typing import List, Tuple


class CodeParser:
    def __init__(self,
                 importing_module_color: str = "#428aff",
                 imported_module_color: str = "#f26d90",
                 disconnected_module_color: str = "#fcb16f",
                 no_colorize_graph: bool = False) -> None:
        self.graph = Graph(strict=True, splines="true", overlap=False,
                           node_style="filled", directed=True)
        self.sub_graphs = defaultdict(list)
        self.graph_dict = defaultdict(dict)
        self.module_count = defaultdict(int)
        self.importing_module_color = importing_module_color
        self.imported_module_color = imported_module_color
        self.disconnected_module_color = disconnected_module_color
        self.no_colorize_graph = no_colorize_graph

    def parse_project(self, directory: str,
                      excluded_directories: List[str],
                      include_external: bool = True,
                      parse_importlib: bool = True,
                      follow_links: bool = True) -> Graph:
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
            for filename in files:
                # Skip non python files
                if not filename.endswith(".py"):
                    continue
                # Skip .pyc and __init__.py files
                if ".pyc" in filename or "__init__.py" in filename:
                    continue

                module_path = os.path.join(root, filename)
                module_dir = os.path.dirname(module_path)
                module_name = module_path.replace(os.path.sep, ".")[:-3]

                self.graph.add_node(module_name, label=module_name)
                cluster_name = "cluster_" + str(os.path.sep.join(module_name.split(".")[:-1]))
                self.sub_graphs[cluster_name].append(module_name)

                with open(module_path, "r") as f:
                    module_tree = ast.parse(f.read())
                    for node in ast.walk(module_tree):
                        if isinstance(node, ast.Import):
                            self.parse_first_form_import(import_node=node,
                                                         importing_module=module_name,
                                                         current_dir=module_dir,
                                                         package_name=directory,
                                                         include_external=include_external)
                        elif isinstance(node, ast.ImportFrom):
                            self.parse_second_form_import(import_node=node,
                                                          importing_module=module_name,
                                                          current_dir=module_dir,
                                                          package_name=directory,
                                                          include_external=include_external)
                        elif isinstance(node, ast.Call) and parse_importlib:
                            if isinstance(node.func, ast.Name) and node.func.id == "import_module":
                                try:
                                    import_node = ast.literal_eval(node.args[0])
                                    package = None if not node.keywords else node.keywords[0]
                                    self.parse_importlib_import(import_node=import_node,
                                                                package=package,
                                                                importing_module=module_name,
                                                                current_dir=module_dir,
                                                                include_external=include_external)
                                except ValueError:
                                    pass
                            elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                                if node.func.value.id == "importlib" and node.func.attr == "import_module":
                                    try:
                                        import_node = ast.literal_eval(node.args[0])
                                        package = None if not node.keywords else node.keywords[0]
                                        self.parse_importlib_import(import_node=import_node,
                                                                    package=package,
                                                                    importing_module=module_name,
                                                                    current_dir=module_dir,
                                                                    include_external=include_external)
                                    except ValueError:
                                        pass

        # Add clusters
        self.graph.add_clusters(self.sub_graphs)
        if not self.no_colorize_graph:
            prettify_graph(graph=self.graph,
                           source_color=self.importing_module_color,
                           sink_color=self.imported_module_color,
                           not_connected_color=self.disconnected_module_color)
        return self.graph

    def parse_first_form_import(self, import_node: ast.AST, package_name: str,
                                importing_module: str, current_dir: str, include_external: bool) -> None:
        for alias in import_node.names:
            imported_module = importlib.util.resolve_name(alias.name, package_name)
            imported_module_as_path = imported_module.replace(".", os.path.sep) + ".py"

            # Check if just replace the dots by "/" and appending ".py" leads to a file
            if os.path.isfile(imported_module_as_path):
                self.graph.add_node(imported_module, label=imported_module)
                self.graph.add_edge(importing_module, imported_module)

            # Check if joining the path to the current directory to the previously generated path leads to a file
            elif os.path.isfile(os.path.join(current_dir, imported_module_as_path)):
                node_name = os.path.join(current_dir, imported_module).replace(os.path.sep, ".")
                self.graph.add_node(node_name, label=imported_module)
                self.graph.add_edge(importing_module, imported_module)

            # Else the module is external to this project and we check the include_external flag
            elif include_external is True:
                self.graph.add_node(imported_module, label=imported_module + " external")
                self.graph.add_edge(importing_module, imported_module)
                root_package = imported_module.split(".")[0]
                cluster_name = "cluster_" + str(root_package)
                self.sub_graphs[cluster_name].append(imported_module)

    def parse_second_form_import(self, import_node: ast.AST, package_name: str,
                                 importing_module: str, current_dir: str, include_external: bool) -> None:
        imported_from_module = importlib.util.resolve_name(import_node.module, package_name)
        is_file, name, label = self.module_is_file(imported_from_module, current_dir)
        if is_file:
            self.graph.add_node(name, label=label)
            self.graph.add_edge(importing_module, name)
        else:
            imported_module_is_file = False
            for imported_module in import_node.names:
                is_file, name, label = self.module_is_file(imported_module.name, current_dir)
                if is_file:
                    imported_module_is_file = True
                    self.graph.add_node(name, label=label)
                    self.graph.add_edge(importing_module, name)
                    if include_external:
                        cluster_name = "cluster_" + str(imported_module.split(".")[0])
                        self.sub_graphs[cluster_name].append(imported_from_module)
            if not imported_module_is_file and include_external:
                self.graph.add_node(imported_from_module, label=imported_from_module)
                self.graph.add_edge(importing_module, imported_from_module)
                cluster_name = "cluster_" + str(imported_from_module.split(".")[0])
                self.sub_graphs[cluster_name].append(imported_from_module)

    def module_is_file(self, imported_module: str, current_dir: str) -> Tuple[bool, str, str]:
        # Helper variables
        file_path = imported_module.replace(".", os.path.sep) + ".py"
        sequence_matcher = SequenceMatcher(None, current_dir, file_path)
        overlap_index, _, overlap_size = sequence_matcher.find_longest_match(0, len(current_dir), 0, len(file_path))
        file_path_overlap = os.path.join(current_dir[:overlap_index], file_path)
        file_path_no_overlap = os.path.join(current_dir, file_path)
        # Check if the imported_from_module when treated as a path (replacing . with /)
        # leads to a python file in this project
        if os.path.isfile(file_path):
            return True, imported_module, imported_module
        # Check if the path formed by joining the current directory and the file path made from the imported_from_module
        # leads to a python file. Once assuming there is overlap between the two and once without.
        elif os.path.isfile(file_path_overlap):
            imported_module = file_path_overlap[:-3].replace(os.path.sep, ".")
            return True, imported_module, imported_module
        elif os.path.isfile(file_path_no_overlap):
            imported_module = file_path_no_overlap[:-3].replace(os.path.sep, ".")
            return True, imported_module, imported_module
        else:
            return False, "", ""

    def parse_importlib_import(self, import_node: ast.AST, package: str, importing_module: str,
                               current_dir: str, include_external: bool) -> None:
        imported_module = import_node
        imported_module = importlib.util.resolve_name(imported_module, package)
        imported_module_as_path = imported_module.replace(".", os.path.sep) + ".py"

        # Check if just replace the dots by "/" and appending ".py" leads to a file
        if os.path.isfile(imported_module_as_path):
            self.graph.add_node(imported_module, label=imported_module)
            self.graph.add_edge(importing_module, imported_module)

        # Check if joining the path to the current directory to the previously generated path leads to a file
        elif os.path.isfile(os.path.join(current_dir, imported_module_as_path)):
            node_name = os.path.join(current_dir, imported_module).replace(os.path.sep, ".")
            self.graph.add_node(node_name, label=imported_module)
            self.graph.add_edge(importing_module, imported_module)

        # Else the module is external to this project and we check the include_external flag
        elif include_external is True:
            self.graph.add_node(imported_module, label=imported_module + " external")
            self.graph.add_edge(importing_module, imported_module)
            root_package = imported_module.split(".")[0]
            cluster_name = "cluster_" + str(root_package)
            self.sub_graphs[cluster_name].append(imported_module)



