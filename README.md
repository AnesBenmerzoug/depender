# Depender

Depender is a Python package that is used to determine the dependency graph
of a given Python project given its path.

![Dependency Graph](/docs/images/dependency_graph.png)

As a bonus, it can also be used to plot a hierarchical diagram 
of the directory structure.

![Structure Graph](/docs/images/directory_structure_graph.png)

## Installation

Since it's not yet available in PyPi, it can only be installed after cloning this repository and running:
```bash
pip install .
```

## Running

To obtain the dependency graph of your project or just part of it run:

```bash
depender dependency <path/to/project>
```

To obtain a graph of the directory structure of a given project run:

```bash
depender structure <path/to/project> --depth 2
```

```depth``` is an optional argument that can be specified when you want to limit the depth of the directory recursion