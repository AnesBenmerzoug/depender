from abc import ABC, abstractmethod
from jinja2 import Environment, PackageLoader
from typing import Optional, Tuple


class GraphRenderer(ABC):
    def __init__(self, output_dir: str, output_format: Optional[str] = None,
                 figure_dimensions: Tuple[float, float] = (1280, 960), dpi: int = 100) -> None:
        self.output_dir = output_dir
        self.output_format = output_format
        self.figure_dimensions = figure_dimensions
        self.dpi = dpi
        jinja_environment = Environment(loader=PackageLoader("depender", "templates"))
        self.template = jinja_environment.get_template("template.html")

    @abstractmethod
    def render_graph(self, graph) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_or_save_figure(self, filename: Optional[str] = None) -> None:
        raise NotImplementedError
