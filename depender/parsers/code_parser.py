import os
import ast
import importlib
import importlib.util
from depender.graph.graph import Graph
from collections import defaultdict

from typing import List


class CodeParser:
    def __init__(self) -> None:
        self.graph = Graph()
        self.sub_graphs = defaultdict(list)

    def parse_project(self, directory: str,
                      excluded_directories: List[str],
                      include_external: bool = True,
                      parse_importlib: bool = True,
                      follow_links: bool = True,
                      depth: int = 5) -> Graph:
        # Remove / if it is at the end of the given directory path
        if directory.endswith(os.path.sep):
            directory = directory[:-1]
        package_root_path = None
        package_name = None
        filelist = list()
        # First traverse the whole directory, up to the given depth, to find the package name
        # Which should correspond to the first directory that contains an __init__.py file
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

            current_depth = root.count(os.path.sep)

            # Don't go deeper than "depth" if it has a non-negative value
            if current_depth > depth >= 0:
                dirs[:] = list()
                files[:] = list()

            if package_root_path is None:
                if "__init__.py" in files:
                    package_root_path = root
                    package_name = os.path.basename(root)
                    break

        # If the package name was not found return
        if package_name is None:
            return self.graph

        # Then traverse the whole directory again, up to the given depth, to find all python modules and files
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

            current_depth = root.count(os.path.sep)

            # Don't go deeper than "depth" if it has a non-negative value
            if current_depth > depth >= 0:
                dirs[:] = list()
                files[:] = list()

            for filename in files:
                # Skip non python files
                if not filename.endswith(".py"):
                    continue
                # Skip .pyc and __init__.py files
                if ".pyc" in filename or "__init__.py" in filename:
                    continue

                if len(package_root_path) > len(root):
                    module_dot_path = "." * (package_root_path.count(os.path.sep) - root.count(os.path.sep) + 1)\
                                      + filename[:-3]
                else:
                    module_dot_path = ".".join(filter(lambda x: bool(x), [package_name,
                                                                          root[len(package_root_path) + 1:],
                                                                          filename[:-3]]))
                filelist.append((os.path.join(root, filename), module_dot_path))
                self.graph.add_node(module_dot_path, label=module_dot_path)

        # Finally traverse only the files that were found
        for filepath, module_dot_path in filelist:
            self.parse_file(filepath, module_dot_path,
                            package_name, include_external,
                            parse_importlib)
        return self.graph

    def parse_file(self, filepath: str, module_dot_path: str,
                   package_name: str, include_external: bool, parse_importlib: bool) -> None:
        with open(filepath, "r") as f:
            module_tree = ast.parse(f.read())
            for node in ast.walk(module_tree):
                if isinstance(node, ast.Import):
                    self.parse_first_form_import(import_node=node,
                                                 importing_module=module_dot_path,
                                                 package_name=package_name,
                                                 include_external=include_external)

                elif isinstance(node, ast.ImportFrom):
                    self.parse_second_form_import(import_node=node,
                                                  importing_module=module_dot_path,
                                                  package_name=package_name,
                                                  include_external=include_external)

                elif isinstance(node, ast.Call) and parse_importlib:
                    if isinstance(node.func, ast.Name) and node.func.id == "import_module":
                        try:
                            import_node = ast.literal_eval(node.args[0])
                            package = None if not node.keywords else node.keywords[0]
                            self.parse_importlib_import(import_node=import_node,
                                                        package=package,
                                                        importing_module=module_dot_path,
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
                                                            importing_module=module_dot_path,
                                                            include_external=include_external)
                            except ValueError:
                                pass

    def parse_first_form_import(self, import_node: ast.AST, package_name: str,
                                importing_module: str, include_external: bool) -> None:
        for alias in import_node.names:
            imported_module = importlib.util.resolve_name(alias.name, package_name)

            # Check if the imported module is in the list of this package's modules
            if self.graph.node_exists(imported_module):
                self.graph.add_node(imported_module, label=imported_module)
                self.graph.add_edge(importing_module, imported_module)

            # Else the module is external to this project and we check the include_external flag
            elif include_external is True:
                package = imported_module.split(".")[0]
                self.graph.add_node(package, label=package + " external")
                self.graph.add_edge(importing_module, package)

    def parse_second_form_import(self, import_node: ast.AST, package_name: str,
                                 importing_module: str, include_external: bool) -> None:
        imported_from_module = importlib.util.resolve_name(import_node.module, package_name)

        # Check if the first part of the from ... import ... is a module
        if self.graph.node_exists(imported_from_module):
            self.graph.add_node(imported_from_module, label=imported_from_module)
            self.graph.add_edge(importing_module, imported_from_module)
        else:
            for imported_module in import_node.names:
                module_dot_path = ".".join([imported_from_module, imported_module.name])
                if self.graph.node_exists(module_dot_path):
                    self.graph.add_node(module_dot_path, label=module_dot_path)
                    self.graph.add_edge(importing_module, module_dot_path)
            if include_external:
                package = imported_from_module.split(".")[0]
                self.graph.add_node(package, label=package)
                self.graph.add_edge(importing_module, package)

    def parse_importlib_import(self, import_node: ast.AST, package: str,
                               importing_module: str, include_external: bool) -> None:
        imported_module = importlib.util.resolve_name(import_node, package)

        # Check if the imported module is in the list of this package's modules
        if self.graph.node_exists(imported_module):
            self.graph.add_node(imported_module, label=imported_module)
            self.graph.add_edge(importing_module, imported_module)

        # Else the module is external to this project and we check the include_external flag
        elif include_external is True:
            package = imported_module.split(".")[0]
            self.graph.add_node(package, label=package + " external")
            self.graph.add_edge(importing_module, package)




