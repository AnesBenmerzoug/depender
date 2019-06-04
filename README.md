# Depender

Depender is a Python package that is used to determine and plot 
the dependencies of a given Python package given its name or its path.

![Dependency Graph](/docs/images/dependency_graph.png)

![Dependency Matrix](/docs/images/dependency_matrix.png)

As a bonus, it can also be used to plot a hierarchical diagram 
of the directory structure of said package.

![Structure Graph](/docs/images/structure_graph.png)

## Installation

### Requirements

Depender requires Python 3.5+

### Install latest release
Using ```pip```:

```bash
pip install depender
```

### Install from source

```bash
git clone https://github.com/AnesBenmerzoug/depender
pip install .
```

## Usage

The package can be used from the command line:

```bash
depender <packageName>
```

or 

```bash
depender --source <packagePath> 
```

```
Usage: depender [OPTIONS] PACKAGE_PATH [EXCLUDED_DIRS]...

  Depender command line interface

  Create a dependency graph, a dependency matrix and/or a directory
  structure graph for a given Python package.

  PROJECT_PATH should be the path (relative or absolute) to the root of the
  Python package.

  EXCLUDED_DIRS should be, if provided, the name of or more directories in
  the package to be excluded from the graph.

Options:
  -o, --output-dir PATH  Output directory  [default: graphs]
  -fmt, --format TEXT    Output format, if specified the graph will be
                         rendered to a file with the given format
  --include-external     When set, external packages are included in the
                         graphs  [default: False]
  --no-follow-links      When set the script visits directories pointed to by
                         symlinks  [default: False]
  --depth INTEGER        Depth of the directory recursion  [default: 5]
  --version              Show the version and exit.
  -h, --help             Show this message and exit.

```

## License

Depender is licensed under the Apache Software License version 2.0.