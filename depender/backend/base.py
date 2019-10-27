from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Tuple, Union

from depender.graph.dependency import DependencyGraph
from depender.graph.structure import StructureGraph


class BaseBackend(ABC):
    def __init__(
        self,
        output_dir: Union[str, Path],
        format: Optional[str] = None,
        figure_dimensions: Tuple[float, float] = (1280, 960),
        dpi: int = 100,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.format = format
        self.figure_dimensions = figure_dimensions
        self.dpi = dpi

    @abstractmethod
    def plot(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def save_to_file(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def plot_dependency_matrix(self, graph: DependencyGraph, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def plot_dependency_graph(self, graph: DependencyGraph, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def plot_structure_graph(self, graph: StructureGraph, **kwargs):
        raise NotImplementedError
