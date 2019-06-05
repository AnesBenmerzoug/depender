import os
from pathlib import Path
from depender.graph.graph import Graph
from typing import List, Tuple, Iterable


def find_all_package_modules(package_path: Path,
                             excluded_directories: List[Path],
                             graph: Graph,
                             depth: int,
                             followlinks: bool):
    file_list = list()
    for root, dirs, files in traverse_directory(package_path,
                                                excluded_directories,
                                                depth=depth, followlinks=followlinks):
        for filename in files:
            # Skip non python files
            if not ".py" == filename.suffix:
                continue
            # Skip  __init__.py files
            if "__init__.py" in filename.name:
                continue
            # Form the dot path relative to the package's path
            relative_path = root.relative_to(package_path.parent)
            relative_path = relative_path.joinpath(filename.stem)
            module_dot_path = ".".join(relative_path.parts)
            file_list.append((root / filename, module_dot_path))
            graph.add_node(module_dot_path, label=module_dot_path)
    return file_list


def traverse_directory(directory: Path,
                       excluded_directories: List[Path],
                       depth: int,
                       followlinks: bool,
                       breadth_first: bool = False) -> Iterable[Tuple[Path, List[Path], List[Path]]]:
    root_depth = len(directory.parents)
    dirlist = list()
    for root, dirs, files in os.walk(directory, followlinks=followlinks):
        root = Path(root)
        # Check to see if there are user specified directories that should be skipped
        if check_if_skip_directory(root, excluded_directories):
            continue
        # Don't go deeper than "depth" if it has a non-negative value
        current_depth = len(root.parents) - root_depth
        if current_depth > depth >= 0:
            continue
        # Convert the dir and filenames to Path instances
        dirs = list(map(lambda dir: Path(dir), dirs))
        files = list(map(lambda file: Path(file), files))
        # Remove directories that start with a '.'
        dirs = skip_hidden_directories(dirs)
        dirlist.append((root, dirs, files))
        # If breadth first is True, sort the paths by directory level
        if breadth_first:
            dirlist = sorted(dirlist, key=lambda x: len(x[0].parents))
    for root, dirs, files in dirlist:
        yield root, dirs, files


def check_if_skip_directory(directory: Path, excluded_directories: List[Path]) -> bool:
    if directory in excluded_directories or "__pycache__" in directory.name:
        return True
    else:
        return False


def skip_hidden_directories(directories: List[Path]) -> List[Path]:
    for directory in directories[:]:
        if str(directory)[0] == ".":
            directories.remove(directory)
    return directories
