import click
from typing import List
from pathlib import Path
from importlib.util import find_spec
from click_spinner import spinner  # type: ignore
from depender.parsers.code import CodeParser
from depender.parsers.structure import StructureParser
from depender.render.structure import StructureRenderer
from depender.render.dependency import DependencyRenderer


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"],
                        ignore_unknown_options=True)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("package-name-or-path", nargs=1)
@click.argument("excluded-dirs", nargs=-1,
                type=click.Path(exists=False, file_okay=False, resolve_path=False))
@click.option("-o", "--output-dir", type=click.Path(exists=False, dir_okay=True, resolve_path=True),
              default="graphs",  show_default=True, help="Output directory")
@click.option("-fmt", "--format", type=click.STRING,
              default=None, show_default=True, help="Output format, if specified the graph will be rendered to a file"
                                                    " with the given format")
@click.option("--dims", "--image-dimensions", type=click.STRING,
              default="800,600", show_default=True, help="Dimensions of the rendered graphs given as 'width,height'")
@click.option("--include-external", type=click.BOOL, default=False, is_flag=True,
              show_default=True, help="When set, external packages are included in the graphs")
@click.option("--no-follow-links", type=click.BOOL, default=False, is_flag=True,
              show_default=True, help="When set the script visits directories pointed to by symlinks")
@click.option("--depth", type=click.INT, default=6,
              show_default=True, help="Depth of the directory recursion")
@click.version_option()
def main(package_name_or_path: str,
         excluded_dirs: List[str],
         output_dir: str,
         format: str,
         image_dimensions: str,
         include_external: bool,
         no_follow_links: bool,
         depth: int) -> None:
    r"""Depender command line interface

    Create a dependency graph, a dependency matrix and/or a directory structure graph for a given Python package.

    PROJECT_PATH should be the path (relative or absolute) to the root of the Python package.

    EXCLUDED_DIRS should be, if provided, the name of or more directories in the package to be excluded from the graph.
    """
    # Try to find the package path
    spec = find_spec(package_name_or_path)
    if spec is not None:
        click.echo(f"Found package {package_name_or_path}")
        package_path = Path(spec.origin).parent
    else:
        package_path = Path(package_name_or_path)
        if not package_path.is_dir():
            raise NotADirectoryError("")
        elif not package_path.joinpath("__init__.py").is_file():
            raise Exception("The given path is not a Python package")
        else:
            click.echo(f"Found package at location {package_name_or_path}")
        package_path = package_path.stem
    # Get the desired image dimensions
    image_width, image_height = map(int, image_dimensions.split(","))
    # Instantiate the parsers
    code_parser = CodeParser()
    structure_parser = StructureParser()
    # Instantiate the Graph renderers
    structure_renderer = StructureRenderer(output_dir=output_dir,
                                           output_format=format,
                                           figure_dimensions=(image_width,
                                                              image_height))
    dependency_renderer = DependencyRenderer(output_dir=output_dir,
                                             output_format=format,
                                             figure_dimensions=(image_width,
                                                                image_height))
    # Parse the package
    click.echo("Parsing package...")
    with spinner():
        code_graph = code_parser.parse_project(package_path=package_path,
                                               excluded_directories=excluded_dirs,
                                               include_external=include_external,
                                               follow_links=not no_follow_links,
                                               depth=depth)
        structure_graph = structure_parser.parse_project(package_path=package_path,
                                                         excluded_directories=excluded_dirs,
                                                         follow_links=not no_follow_links,
                                                         depth=depth)

    # Layout and write to file
    click.echo("Plotting graphs...")
    with spinner():
        dependency_renderer.render_matrix(code_graph)
        dependency_renderer.render_graph(code_graph)
        structure_renderer.render_graph(structure_graph)
    click.echo("Done")


if __name__ == "__main__":
    main()
