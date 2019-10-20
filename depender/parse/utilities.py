import os
from pathlib import Path
from typing import Iterable, List, Tuple


def traverse_directory(
    directory: Path,
    excluded_directories: List[Path],
    depth: int,
    followlinks: bool,
    breadth_first: bool = False,
) -> Iterable[Tuple[Path, List[Path], List[Path]]]:
    root_depth = len(directory.parents)
    dirlist = list()

    for root, dirs, files in os.walk(directory.resolve(), followlinks=followlinks):
        root = Path(root).resolve()
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
