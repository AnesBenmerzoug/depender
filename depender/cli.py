import sys
from importlib.util import find_spec
from pathlib import Path
from typing import List

import click
from click_spinner import spinner  # type: ignore
from depender.backend import get_backend
from depender.parse.code import CodeParser
from depender.parse.structure import StructureParser

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"], ignore_unknown_options=True)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("path-or-name", nargs=1)
@click.argument(
    "excluded-dirs",
    nargs=-1,
    type=click.Path(exists=False, file_okay=False, resolve_path=False),
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=False, dir_okay=True, resolve_path=True),
    default="graphs",
    show_default=True,
    help="Output directory",
)
@click.option(
    "-fmt",
    "--format",
    type=click.STRING,
    default=None,
    show_default=True,
    help="Output format, if specified the graph will be rendered to a file"
    " with the given format",
)
@click.option(
    "--backend",
    type=click.Choice(["graphviz", "matplotlib"]),
    default="graphviz",
    show_default=True,
    help="Backend used for plotting",
)
@click.option(
    "--dims",
    "--image-dimensions",
    type=click.STRING,
    default="800,600",
    show_default=True,
    help="Dimensions of the rendered graphs given as 'width,height'",
)
@click.option(
    "--include-external",
    type=click.BOOL,
    default=False,
    is_flag=True,
    show_default=True,
    help="When set, external packages are included in the graphs",
)
@click.option(
    "--no-follow-links",
    type=click.BOOL,
    default=False,
    is_flag=True,
    show_default=True,
    help="When set the script visits directories pointed to by symlinks",
)
@click.option(
    "--depth",
    type=click.INT,
    default=6,
    show_default=True,
    help="Depth of the directory recursion",
)
@click.version_option()
def main(
    path_or_name: str,
    excluded_dirs: List[str],
    output_dir: str,
    format: str,
    backend: str,
    image_dimensions: str,
    include_external: bool,
    no_follow_links: bool,
    depth: int,
) -> None:
    r"""Depender command line interface

    Create a dependency graph, a dependency matrix and/or a directory structure graph for a given Python package.

    PATH_OR_NAME should be either:
        - the path (relative or absolute) to the root of a Python package or module
        - the name of an installed package

    EXCLUDED_DIRS should be, if provided, the paths relative to the package of one or more directories
    to exclude from the graph.
    """
    try:
        spec = find_spec(path_or_name)
    except ModuleNotFoundError:
        spec = None
    # Try to find the package path
    package_path = Path(path_or_name)
    if package_path.is_file() and package_path.suffix == ".py":
        click.echo(f"Found module at '{package_path.absolute()}'")
        is_module = True
    elif package_path.is_dir() and package_path.joinpath("__init__.py").is_file():
        click.echo(f"Found package at '{package_path.absolute()}'")
        is_module = False
    elif spec is not None:
        package_path = Path(spec.origin)
        if package_path.name == "__init__.py":
            click.echo(f"Found package '{path_or_name}'")
            package_path = package_path.parent
            is_module = False
        else:
            click.echo(f"Found module '{path_or_name}'")
            is_module = True
    else:
        click.echo(f"Could not find a package or a module at '{package_path}'")
        sys.exit(1)
    # Get the desired image dimensions
    image_width, image_height = map(int, image_dimensions.split(","))
    # Instantiate the parsers
    code_parser = CodeParser()
    structure_parser = StructureParser()
    # Instantiate the backend
    backend = get_backend("backend")(
        output_dir=output_dir,
        format=format,
        figure_dimensions=(image_width, image_height),
    )
    click.echo("Parsing package...")
    with spinner():
        code_graph = code_parser.parse_project(
            package_path=package_path,
            is_module=is_module,
            excluded_directories=excluded_dirs,
            include_external=include_external,
            follow_links=not no_follow_links,
        )
        structure_graph = structure_parser.parse_project(
            package_path=package_path,
            excluded_directories=excluded_dirs,
            follow_links=not no_follow_links,
            depth=depth,
        )
    # Layout and write to file
    click.echo("Plotting graphs...")
    with spinner():
        backend.plot_dependency_matrix(code_graph)
        backend.plot_dependency_graph(code_graph)
        backend.plot_structure_graph(structure_graph)
    click.echo("Done")


if __name__ == "__main__":
    main()
