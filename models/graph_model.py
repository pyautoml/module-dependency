from os import path
from pathlib import Path
from seaborn import heatmap
from pandas import DataFrame
from networkx import DiGraph
from numpy import ndarray, zeros
from typing import List, Tuple, Optional
from pydantic import BaseModel, ConfigDict, Field
from .abstract_models.abstract_graph_model import AbstractGraphModel
from matplotlib.pyplot import savefig, figure, title, xlabel, ylabel, xticks, yticks, tight_layout, show


class GraphModel(BaseModel, AbstractGraphModel):
    data: List[dict]
    graph: Optional[DiGraph] = DiGraph()
    top_n_imports: Optional[int] = Field(default=0)
    is_built: Optional[bool] = Field(default=False)
    nodes: Optional[List[str]] = Field(default_factory=list)
    paths: Optional[List[str]] = Field(default_factory=list)
    adjacency_matrix: Optional[ndarray] = Field(default=None)
    imports: Optional[List[str]] = Field(default_factory=list)
    edges: Optional[List[Tuple[str, str]]] = Field(default_factory=list)
    model_config: Optional[ConfigDict] = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        if not isinstance(self.top_n_imports, int):
            self.top_n_imports = 0
            
        self.__build()

    # -------------------
    # protected methods
    # -------------------
    @staticmethod
    def __join_paths(file_path: str, file: str) -> str:
        return path.join(Path(file_path).as_posix(), Path(file).as_posix())
    
    def __validate_file_name(self, file_name: str) -> str:
        if not file_name or not isinstance(file_name, str | Path):
            file_name: str = "imports_dependency.png"
        file_name: str = f"{file_name}"
        if "." not in file_name:
            file_name = file_name + ".png"
        return file_name.replace(" ", "_")

    def __get_nodes(self) -> List[str]:
        return list(self.graph.nodes)

    def __get_edges(self) -> List[Tuple[str, str]]:
        return list(self.graph.edges)

    def __to_edge_list(self) -> DataFrame:
        if self.is_built:
            return DataFrame(self.edges, columns=["source", "target"])
        return DataFrame(columns=["source", "target"])

    def __get_paths_and_imports(self) -> Tuple[List[str], List[str]]:
        paths = sorted(set(edge[0] for edge in self.edges))
        imports = sorted(set(edge[1] for edge in self.edges))
        return paths, imports

    def __to_custom_adjacency_matrix(self) -> ndarray:
        paths, imports = self.__get_paths_and_imports()
        
        if self.top_n_imports > 0:
            paths = paths[:self.top_n_imports]
            imports = imports[:self.top_n_imports]
            
        matrix = zeros((len(paths), len(imports)))
        for i, p in enumerate(paths):
            for j, imp in enumerate(imports):
                if self.graph.has_edge(p, imp):
                    matrix[i, j] = 1
        return matrix, paths, imports
    
    def __build(self) -> DiGraph:
        for dep in self.data:
            file = dep['file']
            imported_module = dep['import']
            if isinstance(imported_module, list):
                for module in imported_module:
                    self.graph.add_edge(file, module)
            else:
                self.graph.add_edge(file, imported_module)

        self.nodes = self.__get_nodes()
        self.edges = self.__get_edges()
        self.adjacency_matrix, self.paths, self.imports = self.__to_custom_adjacency_matrix()
        self.is_built = True
        return self.graph

    # ----------------
    # public methods
    # ----------------
    def display(
            self,
            figure_size: Optional[Tuple[int, int]] = (15, 15),
            img_title: Optional[str] = "Adjacency Matrix",
            xlabel_tag: Optional[str] = "Imports",
            ylabel_tag: Optional[str] = "Paths",
            rotation: Optional[int] = 90,
            fontsize: Optional[int] = 8,
            cbar: Optional[bool] = True,
    ) -> None:
        if not self.is_built:
            raise RuntimeError("The graph must be built using the '__build()' method before calling 'display()'.")

        figure(figsize=figure_size)
        heatmap(
            self.adjacency_matrix, 
            annot=True, fmt="g", 
            cmap='viridis', 
            xticklabels=self.imports, 
            yticklabels=self.paths,
            cbar=cbar
        )
        title(img_title)
        xlabel(xlabel_tag)
        ylabel(ylabel_tag)
        xticks(rotation=rotation, fontsize=fontsize)
        yticks(fontsize=fontsize)
        tight_layout()
        show()

    def save(            
        self,
        local_save_path: str,
        figure_size: Optional[Tuple[int, int]] = (15, 15),
        img_title: Optional[str] = "Adjacency Matrix",
        file_name: Optional[str] = "imports_dependency.png",
        xlabel_tag: Optional[str] = "Imports",
        ylabel_tag: Optional[str] = "Paths",
        rotation: Optional[int] = 90,
        fontsize: Optional[int] = 8,
        cbar: Optional[bool] = True
    ) -> None:
        if not self.is_built:
            raise RuntimeError("The graph must be built using the '__sbuild()' method before calling 'save()'.")

        figure(figsize=figure_size)
        heatmap(
            self.adjacency_matrix, 
            annot=True, 
            fmt="g", 
            cmap='viridis', 
            xticklabels=self.imports, 
            yticklabels=self.paths,
            cbar=cbar
        )
        title(img_title)
        xlabel(xlabel_tag)
        ylabel(ylabel_tag)
        xticks(rotation=rotation, fontsize=fontsize)
        yticks(fontsize=fontsize)
        tight_layout()
        file_name: str = self.__validate_file_name(file_name)
        savefig(self.__join_paths(local_save_path, file_name), format="png")
    
    def list_edges(self) -> list:
        return self.__to_edge_list()
