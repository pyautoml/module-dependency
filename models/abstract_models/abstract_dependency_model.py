from typing import Tuple, Optional
from abc import ABC, abstractmethod


class AbstractDependencyModel(ABC):

    @abstractmethod
    def build_graph(
            self, 
            remove_from_root_path: Optional[str] = None, 
            import_type: Optional[str] = "custom"
        ) -> None:
        pass

    @abstractmethod
    def save_graph_matrix(            
        self,
        local_save_path: str,
        figure_size: Optional[Tuple[int, int]] = (15, 15),
        img_title: Optional[str] = "Adjacency Matrix",
        file_name: Optional[str] = "imports_dependency.png",
        xlabel_tag: Optional[str] = "Imports",
        ylabel_tag: Optional[str] = "Paths",
        rotation: Optional[int] = 90,
        fontsize: Optional[int] = 8,
        cbar: Optional[bool] = True,
    ):
        pass
