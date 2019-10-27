from abc import ABC, abstractmethod
from typing import Optional, Tuple

from depender.graph.dependency import DependencyGraph
from depender.graph.structure import StructureGraph


class BaseBackend(ABC):
    def __init__(
        self,
        output_dir: str,
        output_format: Optional[str] = None,
        figure_dimensions: Tuple[float, float] = (1280, 960),
        dpi: int = 100,
    ) -> None:
        self.output_dir = output_dir
        self.output_format = output_format
        self.figure_dimensions = figure_dimensions
        self.dpi = dpi

    @abstractmethod
    def plot_dependency_matrix(self, graph: DependencyGraph, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    def plot_dependency_graph(self, graph: DependencyGraph, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def plot_structure_graph(self, graph: StructureGraph, **kwargs):
        raise NotImplementedError
