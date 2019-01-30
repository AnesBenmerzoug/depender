import click
from typing import List
from depender.parsers.code_parser import CodeParser
from depender.parsers.structure_parser import StructureParser

from importlib import import_module
import_module("os")


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"],
                        ignore_unknown_options=True)


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option()
def main():
    r"""
    Depender command line interface

    """
    pass


@main.command(name="dependency", short_help="create dependency graph")
@click.version_option()
@click.argument("project-path", nargs=1, type=click.Path(exists=True, file_okay=False, resolve_path=False))
@click.argument("excluded-dirs", nargs=-1, type=click.Path(exists=False, file_okay=False, resolve_path=False))
@click.option("--include-external", type=click.BOOL, default=False, is_flag=True)
@click.option("--no-follow-links", type=click.BOOL, default=False, is_flag=True,
              help="When set the script visits directories pointed to by symlinks")
@click.option("-o", "--output_file", type=click.Path(exists=False, dir_okay=False, resolve_path=False),
              default=None, help="Output file")
@click.option("--fmt", "--format", "format", type=click.STRING, default="pdf",
              help="Format in which to store the graph. Default 'pdf'")
@click.option("--engine", type=click.STRING, default="fdp",
              help="Graphviz layout engine used to draw the graph. Default 'fdp'")
@click.option("--importing-module-color", type=click.STRING, default="#428AFF",
              help="Color of the modules that only import other modules")
@click.option("--imported-module-color", type=click.STRING, default="#F26D90",
              help="Color of the modules that are only imported by other modules")
@click.option("--disconnected-module-color", default="#FCB16F", type=click.STRING,
              help="Color of the modules that are neither imported nor import other modules")
@click.option("--no-colorize-graph", type=click.BOOL, default=False, is_flag=True,
              help="When set the resulting graph is not colorized")
def dependency_graph(project_path: str, excluded_dirs: List[str],
                     include_external: bool, no_follow_links: bool,
                     output_file: str, format: str, engine: str,
                     importing_module_color: str, imported_module_color: str,
                     disconnected_module_color: str, no_colorize_graph: bool) -> None:
    r"""
    Create dependency graph for a given Python project.

    PROJECT_PATH should be the path (relative or absolute) to the Python project.

    EXCLUDED_DIRS should be, if provided, the name of or more directories in the project to be excluded from the graph.

    """
    # Instantiate the parser
    parser = CodeParser(importing_module_color=importing_module_color,
                        imported_module_color=imported_module_color,
                        disconnected_module_color=disconnected_module_color,
                        no_colorize_graph=no_colorize_graph)
    # Parse the project
    graph = parser.parse_project(directory=project_path,
                                 excluded_directories=excluded_dirs,
                                 include_external=include_external,
                                 follow_links=not no_follow_links)
    # Layout and write to file
    output_file = "dependency_graph.{format}".format(format=format) if not output_file \
        else output_file + ".{format}".format(format=format)
    graph.draw(output_file, prog=engine, format=format)


@main.command(name="structure", short_help="create directory structure graph")
@click.argument("project-path", nargs=1, type=click.Path(exists=True, file_okay=False, resolve_path=False))
@click.argument("excluded_dirs", nargs=-1, type=click.Path(exists=False, file_okay=False, resolve_path=False))
@click.option("-o", "--output_file", type=click.Path(exists=False, dir_okay=False, resolve_path=False),
              default=None, help="Output file")
@click.option("--depth", type=click.INT, default=-1,
              help="Depth of the directory recursion")
@click.option("--no-follow-links", type=click.BOOL, default=False, is_flag=True,
              help="When set the script visits directories pointed to by symlinks")
@click.option("--fmt", "--format", "format", type=click.STRING, default="pdf",
              help="Format in which to store the graph. Default 'pdf'")
@click.option("--engine", type=click.STRING, default="dot",
              help="Graphviz layout engine used to draw the graph. Default 'dot'")
@click.option("--root-dir-color", type=click.STRING, default="#377FB4",
              help="Color of the root directory")
@click.option("--dir-color", type=click.STRING, default="#82CBBA",
              help="Color of non-root directories")
@click.option("--file-color", type=click.STRING, default="#ECF7B3",
              help="Color of files")
@click.version_option()
def structure_graph(project_path: str, excluded_dirs: List[str],
                    no_follow_links: bool, depth: int,
                    output_file: str, format: str, engine: str,
                    root_dir_color: str, dir_color: str, file_color: str):
    r"""
    Create directory structure graph for a given Python project

    PROJECT_PATH should be the path (relative or absolute) to the root of the Python project.

    EXCLUDED_DIRS should be, if provided, the name of or more directories in the project to be excluded from the graph.

    """
    # Instantiate the parser
    parser = StructureParser(root_dir_color=root_dir_color,
                             dir_color=dir_color,
                             file_color=file_color)
    # Parse the project
    graph = parser.parse_project(directory=project_path,
                                 excluded_directories=excluded_dirs,
                                 follow_links=not no_follow_links,
                                 depth=depth)
    # Layout and write to file
    output_file = "directory_structure_graph.{format}".format(format=format) if not output_file \
        else output_file + ".{format}".format(format=format)
    graph.draw(output_file, prog=engine, format=format)


if __name__ == "__main__":
    main()
