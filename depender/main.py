import click
from typing import List
from click_spinner import spinner
from depender.parsers.code_parser import CodeParser
from depender.parsers.structure_parser import StructureParser
from depender.graph.render import GraphRenderer


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"],
                        ignore_unknown_options=True)


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("project-path", nargs=1, type=click.Path(exists=True, file_okay=False, resolve_path=False))
@click.argument("excluded-dirs", nargs=-1, type=click.Path(exists=False, file_okay=False, resolve_path=False))
@click.option("-o", "--output-dir", type=click.Path(exists=False, dir_okay=True, resolve_path=True),
              default="html",  show_default=True, help="Output directory")
@click.option("--include-external", type=click.BOOL, default=False, is_flag=True,
              show_default=True, help="When set, external packages are included in the graphs")
@click.option("--no-follow-links", type=click.BOOL, default=False, is_flag=True,
              show_default=True, help="When set the script visits directories pointed to by symlinks")
@click.option("--depth", type=click.INT, default=5,
              show_default=True, help="Depth of the directory recursion")
@click.option("--importing-module-color", type=click.STRING, default="#428AFF",
              show_default=True, help="Color of the modules that only import other modules")
@click.option("--imported-module-color", type=click.STRING, default="#F26D90",
              show_default=True, help="Color of the modules that are only imported by other modules")
@click.option("--disconnected-module-color", default="#FCB16F", type=click.STRING,
              show_default=True, help="Color of the modules that are neither imported nor import other modules")
@click.option("--root-dir-color", type=click.STRING, default="#377FB4",
              show_default=True, help="Color of a root directory node")
@click.option("--dir-color", type=click.STRING, default="#82CBBA",
              show_default=True, help="Color of a non-root directory node")
@click.option("--file-color", type=click.STRING, default="#ECF7B3",
              show_default=True, help="Color of a file node")
@click.version_option()
def main(project_path: str, excluded_dirs: List[str], output_dir: str,
         include_external: bool, no_follow_links: bool, depth: int,
         importing_module_color: str, imported_module_color: str,
         disconnected_module_color: str, root_dir_color: str,
         dir_color: str, file_color: str) -> None:
    r"""
    Depender command line interface

    Create a dependency graph, a dependency matrix and/or a directory structure graph for a given Python project.

    PROJECT_PATH should be the path (relative or absolute) to the root of the Python project.

    EXCLUDED_DIRS should be, if provided, the name of or more directories in the project to be excluded from the graph.

    """
    # Instantiate the parsers
    code_parser = CodeParser()
    structure_parser = StructureParser()
    # Instantiate the Graph renderer
    graph_renderer = GraphRenderer(out_color=importing_module_color,
                                   in_color=imported_module_color,
                                   dis_color=disconnected_module_color,
                                   root_dir_color=root_dir_color,
                                   dir_color=dir_color,
                                   file_color=file_color,
                                   output_dir=output_dir)
    # Parse the project
    click.echo("Parsing project...")
    with spinner():
        code_graph = code_parser.parse_project(directory=project_path,
                                               excluded_directories=excluded_dirs,
                                               include_external=include_external,
                                               follow_links=not no_follow_links,
                                               depth=depth)
        structure_graph = structure_parser.parse_project(directory=project_path,
                                                         excluded_directories=excluded_dirs,
                                                         follow_links=not no_follow_links,
                                                         depth=depth)

    # Layout and write to file
    click.echo("Plotting graphs...")
    with spinner():
        graph_renderer.render_dependency_matrix(graph=code_graph)
        graph_renderer.render_dependency_graph(graph=code_graph)
        graph_renderer.render_structure_graph(graph=structure_graph)
    click.echo("Done")


if __name__ == "__main__":
    main()
