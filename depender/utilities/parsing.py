import os
from depender.graph.graph import Graph
from typing import List, Tuple, Iterable, Optional


def check_if_skip_directory(directory: str, excluded_directories: List[str]) -> bool:
    skip = False
    if excluded_directories is not None:
        for folder_to_exclude in excluded_directories:
            if os.path.sep + folder_to_exclude in directory:
                skip = True
                break
    if skip is True or "__pycache__" in directory:
        return True
    else:
        return False


def traverse_directory(root_directory: str,
                       excluded_directories: List[str],
                       depth: int,
                       followlinks: bool,
                       breadth_first: bool = False) -> Iterable[Tuple[str, List[str], List[str]]]:
    if breadth_first:
        dirlist = [(root, dirs, files)
                   for root, dirs, files in os.walk(root_directory, followlinks=followlinks)
                   if root.count(os.path.sep) <= depth or depth < 0]
        dirlist = sorted(dirlist, key=lambda x: x[0].count(os.path.sep))
        for root, dirs, files in dirlist:
            yield root, dirs, files
    else:
        for root, dirs, files in os.walk(root_directory, followlinks=followlinks):
            # Check to see if there are user specified directories that should be skipped
            if check_if_skip_directory(root, excluded_directories):
                continue
            current_depth = root.count(os.path.sep)
            # Don't go deeper than "depth" if it has a non-negative value
            if current_depth > depth >= 0:
                dirs[:] = list()
                files[:] = list()
            yield root, dirs, files


def find_root_package(root_directory: str,
                      excluded_directories: List[str],
                      depth: int,
                      followlinks: bool) -> Tuple[Optional[str], Optional[str]]:
    package_root_path = None
    package_name = None
    for root, dirs, files in traverse_directory(root_directory,
                                                excluded_directories,
                                                depth=depth, followlinks=followlinks,
                                                breadth_first=True):
        if package_root_path is None:
            if "__init__.py" in files:
                package_root_path = root
                package_name = os.path.basename(root)
                break
    return package_name, package_root_path


def find_all_package_modules(package_root_path: str,
                             package_name: str,
                             graph: Graph,
                             excluded_directories: List[str],
                             depth: int,
                             followlinks: bool):
    file_list = list()
    for root, dirs, files in traverse_directory(package_root_path,
                                                excluded_directories,
                                                depth=depth, followlinks=followlinks):
        for filename in files:
            # Skip non python files
            if not filename.endswith(".py"):
                continue
            # Skip .pyc and __init__.py files
            if ".pyc" in filename or "__init__.py" in filename:
                continue

            # Form the dot path relative to the package's root path
            if len(package_root_path) > len(root):
                module_dot_path = "." * (package_root_path.count(os.path.sep) - root.count(os.path.sep) + 1) \
                                  + filename[:-3]
            else:
                module_dot_path = ".".join(filter(lambda x: bool(x), [package_name,
                                                                      root[len(package_root_path) + 1:],
                                                                      filename[:-3]]))
            file_list.append((os.path.join(root, filename), module_dot_path))
            graph.add_node(module_dot_path, label=module_dot_path)
    return file_list
