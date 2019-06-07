########
Depender
########

|Version| |License|

Depender is a Python package that is used to determine and plot
the dependencies of a given Python package given its name or its path.


.. image:: https://raw.githubusercontent.com/AnesBenmerzoug/depender/master/docs/images/dependency_graph.png
    :align: center
    :alt: Dependency Graph

.. image:: https://raw.githubusercontent.com/AnesBenmerzoug/depender/master/docs/images/dependency_matrix.png
    :align: center
    :alt: Dependency Matrix

As a bonus, it can also be used to plot a hierarchical diagram
of the directory structure of said package.

.. image:: https://raw.githubusercontent.com/AnesBenmerzoug/depender/master/docs/images/structure_graph.png
    :align: center
    :alt: Structure Graph

************
Installation
************

Requirements
============

Depender requires Python 3.5+

Install latest release
----------------------

Using pip:

.. code-block::

    pip install depender

Install from source
-------------------

.. code-block::

    git clone https://github.com/AnesBenmerzoug/depender
    pip install .

*****
Usage
*****

The package can be used from the command line:

.. code-block::

    depender <packageNameOrPath>

.. code-block::

    Usage: depender [OPTIONS] PACKAGE_NAME_OR_PATH [EXCLUDED_DIRS]...

      Depender command line interface

      Create a dependency graph, a dependency matrix and/or a directory
      structure graph for a given Python package.

      PROJECT_PATH should be the path (relative or absolute) to the root of the
      Python package.

      EXCLUDED_DIRS should be, if provided, the name of or more directories in
      the package to be excluded from the graph.

    Options:
      -o, --output-dir PATH           Output directory  [default: graphs]
      -fmt, --format TEXT             Output format, if specified the graph will
                                      be rendered to a file with the given format
      --dims, --image-dimensions TEXT
                                      Dimensions of the rendered graphs given as
                                      'width,height'  [default: 800,600]
      --include-external              When set, external packages are included in
                                      the graphs  [default: False]
      --no-follow-links               When set the script visits directories
                                      pointed to by symlinks  [default: False]
      --depth INTEGER                 Depth of the directory recursion  [default:
                                      6]
      --version                       Show the version and exit.
      -h, --help                      Show this message and exit.


*******
License
*******

Depender is licensed under the Apache Software License version 2.0.


.. |Version| image:: https://img.shields.io/pypi/v/depender.svg
   :target: https://pypi.python.org/pypi/depender/

.. |License| image:: https://img.shields.io/badge/License-Apache%202.0-blue.svg
   :target: https://opensource.org/licenses/Apache-2.0

