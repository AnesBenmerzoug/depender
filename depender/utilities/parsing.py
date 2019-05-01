import os
from depender.graph.graph import Graph
from typing import List, Tuple, Iterable, Optional


def check_if_skip_directory(directory: str, excluded_directories: List[str]) -> bool:
    skip = False
    if directory in excluded_directories or "__pycache__" in directory:
        skip = True
    return skip


def skip_hidden_directories(directories: List[str]) -> List[str]:
    copy_of_directories = directories[:]
    for directory in copy_of_directories:
        if directory.startswith("."):
            directories.remove(directory)
    return directories


def traverse_directory(root_directory: str,
                       excluded_directories: List[str],
                       depth: int,
                       followlinks: bool,
                       breadth_first: bool = False) -> Iterable[Tuple[str, List[str], List[str]]]:
    root_depth = root_directory.count(os.path.sep)
    dirlist = list()
    for root, dirs, files in os.walk(root_directory, followlinks=followlinks):
        # Check to see if there are user specified directories that should be skipped
        if check_if_skip_directory(root, excluded_directories):
            continue
        # Don't go deeper than "depth" if it has a non-negative value
        current_depth = root.count(os.path.sep) - root_depth
        if current_depth > depth >= 0:
            continue
        dirs = skip_hidden_directories(dirs)
        dirlist.append((root, dirs, files))
        if breadth_first:
            dirlist = sorted(dirlist, key=lambda x: x[0].count(os.path.sep))
    for root, dirs, files in dirlist:
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
