from pathlib import Path
import sys
from depender.main import parse_dependencies, parse_structure

to_module = None
if len(sys.argv) > 2 and not sys.argv[2] == '-':
    to_module = sys.argv[2]

excluded_paths = []
if len(sys.argv) > 3:   
    excluded_paths = [Path(path).resolve() for path in sys.argv[3:]]

print(excluded_paths)
parse_dependencies(Path(sys.argv[1]), to_module, excluded_paths)