from __future__ import annotations
from ast import Import
from importlib.util import find_spec
from pathlib import Path
from typing import Optional
from depender.backend import get_backend
from depender.parse.code import CodeParser
from depender.parse.structure import StructureParser


def parse_structure(package_path: Path, excluded_dirs: list[Path | str]):
    structure_parser = StructureParser()
    structure_graph = structure_parser.parse_project(
            package_path=package_path,
            excluded_directories=excluded_dirs,
            depth=100,
        )
    get_backend('matplotlib')(output_dir=package_path).plot_structure_graph(structure_graph)

def parse_dependencies(package_path: Path, to_module: Optional[str] = None, excluded_paths: list[Path] = []):
    code_parser = CodeParser(directed=to_module is None)

    try:
        spec = find_spec(str(package_path))
    except (ModuleNotFoundError, ImportError):
        spec = None

    
    is_module = False
    package_path = Path(package_path)
    if package_path.is_file() and package_path.suffix == ".py":
        is_module = True
    elif package_path.is_dir() and package_path.joinpath("__init__.py").is_file():
        is_module = False
    elif spec is not None:
        package_path = Path(spec.origin)
        if package_path.name == "__init__.py":
            package_path = package_path.parent
            is_module = False
        else:
            is_module = True

    code_graph = code_parser.parse_project(
        package_path=package_path,
        is_module=is_module,
        excluded_directories=excluded_paths,
        include_external=True,
        follow_links=True,
    )
    # for node in code_graph.nodes:
    #     print(node)

    # print('-' * 100)

    # for edge in code_graph.edges:
    #     print(edge)

    print('-' * 100)
    print(f'Number of modules: {len(code_graph.nodes)}')
    if to_module:
        print(f'Number of nodes directly depending on {to_module}: {len(list(code_graph.neighbors(to_module)))}')

        for neighbor in code_graph.neighbors(to_module):
            print(neighbor)
