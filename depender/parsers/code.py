import ast
import importlib
import importlib.util
from pathlib import Path
from depender.graph.graph import Graph
from depender.utilities.parsing import find_all_package_modules
from typing import List, Union


class CodeParser:
    def __init__(self) -> None:
        self.graph = Graph()

    def parse_project(self, package_path: Union[str, Path],
                      excluded_directories: List[Union[str, Path]],
                      include_external: bool = True,
                      parse_importlib: bool = True,
                      follow_links: bool = True,
                      depth: int = 5) -> Graph:
        if isinstance(package_path, str):
            package_path = Path(package_path)
        # Convert the excluded dirs to Path instances
        excluded_directories = list(map(lambda x: package_path.joinpath(x).resolve(),
                                        excluded_directories))
        # If there is no __init__.py file at the given package path then return an empty graph
        if not package_path.joinpath("__init__.py").is_file():
            return self.graph
        package_name = package_path.stem
        # Traverse the whole directory, up to the given depth, to find all python modules and files
        file_list = find_all_package_modules(package_path,
                                             excluded_directories,
                                             self.graph,
                                             depth=depth,
                                             followlinks=follow_links)
        # Finally traverse only the files that were found
        for filepath, module_dot_path in file_list:
            self.parse_file(filepath, module_dot_path,
                            package_name, include_external,
                            parse_importlib)
        return self.graph

    def parse_file(self,
                   filepath: Path,
                   module_dot_path: str,
                   package_name: str,
                   include_external: bool,
                   parse_importlib: bool) -> None:
        with filepath.open("r") as f:
            module_tree = ast.parse(f.read())
            for node in ast.walk(module_tree):
                if isinstance(node, ast.Import):
                    self.parse_first_form_import(import_node=node,
                                                 importing_module=module_dot_path,
                                                 package_name=package_name,
                                                 include_external=include_external)

                elif isinstance(node, ast.ImportFrom):
                    # In case the import is of the form: from . import foo
                    # Then the module attribute is set to None and so we treat the import
                    # as an import of the first form
                    if node.module is None:
                        self.parse_first_form_import(import_node=node,
                                                     importing_module=module_dot_path,
                                                     package_name=package_name,
                                                     include_external=include_external)
                    else:
                        self.parse_second_form_import(import_node=node,
                                                      importing_module=module_dot_path,
                                                      package_name=package_name,
                                                      include_external=include_external)

                elif isinstance(node, ast.Call) and parse_importlib:
                    if isinstance(node.func, ast.Name) and node.func.id == "import_module":
                        try:
                            import_node = str(ast.literal_eval(node.args[0]))
                            package = ""
                            if node.keywords and node.keywords[0].arg:
                                package = node.keywords[0].arg
                            self.parse_importlib_import(import_node=import_node,
                                                        package=package,
                                                        importing_module=module_dot_path,
                                                        include_external=include_external)
                        except ValueError:
                            pass
                    elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                        if node.func.value.id == "importlib" and node.func.attr == "import_module":
                            try:
                                import_node = str(ast.literal_eval(node.args[0]))
                                package = ""
                                if node.keywords and node.keywords[0].arg:
                                    package = node.keywords[0].arg
                                self.parse_importlib_import(import_node=import_node,
                                                            package=package,
                                                            importing_module=module_dot_path,
                                                            include_external=include_external)
                            except ValueError:
                                pass

    def parse_first_form_import(self,
                                import_node: Union[ast.Import, ast.ImportFrom],
                                package_name: str,
                                importing_module: str,
                                include_external: bool) -> None:
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

    def parse_second_form_import(self,
                                 import_node: ast.ImportFrom,
                                 package_name: str,
                                 importing_module: str,
                                 include_external: bool) -> None:
        imported_from_module = importlib.util.resolve_name(import_node.module, package_name)  # type: ignore

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

    def parse_importlib_import(self,
                               import_node: str,
                               package: str,
                               importing_module: str,
                               include_external: bool) -> None:
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




