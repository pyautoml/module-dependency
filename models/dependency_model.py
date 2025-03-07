from json import dumps
from gc import collect
from pathlib import Path
from itertools import islice
from pydantic import BaseModel, ConfigDict, Field
from typing import Tuple, Generator, List, Type, Optional
from .abstract_models.abstract_graph_model import AbstractGraphModel
from .abstract_models.abstract_import_model import AbstractImportModel
from .abstract_models.abstract_dependency_model import AbstractDependencyModel
from .abstract_models.abstract_file_reader_model import AbstractFileReaderModel
from .abstract_models.abstract_file_collector_model import AbstractFileCollectorModel


class DependencyModel(BaseModel, AbstractDependencyModel):
    graph_class: Type[AbstractGraphModel]
    file_collector: AbstractFileCollectorModel
    file_import_class: Type[AbstractImportModel]
    file_reader_class: Type[AbstractFileReaderModel]
    top_n_imports: Optional[int] = Field(default=0)
    model_config = ConfigDict(arbitrary_types_allowed=True)
    root_directory: Optional[str | Path] = str(Path.cwd().parent.as_posix())
    extension: Optional[str] = Field(default=".py")
    exclude_start_characters: str = Field(default=None)
    exclude_end_characters: str = Field(default=None)
    imports: dict = Field(default_factory=dict)
    graph_instance: AbstractGraphModel = Field(default=None)
    import_type: Optional[str] = Field(default=None)
    remove_from_root_path: str = Field(default=None)
    autobuild: bool = Field(default=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.import_type:
            self.import_type = "all"

        if not self.root_directory:
            self.root_directory = Path.cwd().as_posix()
        self.__run()

        if self.autobuild:
            self.build_graph()

    def __run(self) -> str:
        collected_paths: List[str] = self.file_collector.collect_files(
            root_path=self.root_directory,
            extension=self.extension,
            exclude_start_characters=self.exclude_start_characters,
            exclude_end_characters=self.exclude_end_characters,
            return_files=True
        )

        for path in collected_paths:
            if path:
                reader = self.file_reader_class(file_path=path)
                imports: List[str | None] = reader.get_imports()
                import_model = self.file_import_class(imports=imports)
                self.__add_imports(path=path, imports=import_model.get_libraries(as_json=False))
                del import_model
                collect()
    

    def __path_to_posix(self, path: str) -> str:
        try:
            return str(Path(path).as_posix())
        except Exception as e:
            raise Exception(f"Failed to change path to posix value. Provided path is not a valid string: {e}")

    def __filter_by_path(self, path: str) -> dict:
        path = self.__path_to_posix(path)
        return self.imports.get(path, {})

    def __iterate_by_values(self, items: dict, file: str, module: str, module_type: str) -> Generator:
        """items.values() is a List[List[str]] and needs to be flattened."""
        for item in sum(items.values(), []):
            if item == module:
                yield {"file": file, "module": module, "type": module_type}

    def __add_imports(self, path: str, imports: dict):
        if path not in self.imports:
            self.imports[path] = imports
        else:
            self.imports[path]["standard"].extend(imports["standard"])
            self.imports[path]["custom"].extend(imports["custom"])

    def __modify_root_path(self, file_path: str, remove_from_root_path: Optional[str] = None) -> str:
        if remove_from_root_path:
            return file_path.replace(remove_from_root_path, "")
        return file_path

    def __parse_imports_for_graph(
            self, 
            import_type: Optional[str] = "custom", 
            remove_from_root_path: Optional[str] = None
        ) -> Generator:
        if import_type not in ["standard", "custom"]:
            import_type = "custom"

        for full_path, data in self.imports.items():
            data = data[import_type]
            full_path = self.__modify_root_path(full_path, remove_from_root_path)
            if data:
                for k, v in data.items():
                    if not v:
                        yield {"file": full_path, "import": "*"}
                    else:
                        for module in v:
                            yield {"file": full_path, "import": module}

    # ----------------
    # public methods
    # ----------------
    def peek(self, number_of_elements: Optional[int] = 3, as_json: Optional[bool] = False) -> dict:
        data = {k: self.imports[k] for k in islice(self.imports, number_of_elements)}
        return dumps(data, indent=4) if as_json else data

    def get_all_paths(self, sorted_keys: Optional[bool] = False) -> list:
        return sorted(self.imports.keys()) if sorted_keys else list(self.imports.keys())

    def find_imports_by_path(self, path: str = None) -> dict:
        return self.__filter_by_path(path) if path else {}

    def find_by_library(self, library: Optional[str] = None, file_only: Optional[bool] = False) -> Generator:
        if library:
            library = library.strip()
            for key, value in self.imports.items():
                for k in value["standard"].keys():
                    if k == library:
                        yield {"file": key, "import": library, "type": "standard"}
                for k in value["custom"].keys():
                    if k == library:
                        yield {"file": key, "import": library, "type": "custom"}

    def find_by_module(self, module: Optional[str] = None, file_only: Optional[bool] = False) -> Generator:
        if module:
            module = module.strip()
            for key, value in self.imports.items():
                yield from self.__iterate_by_values(items=value["standard"], file=key, module=module, module_type="standard")
                yield from self.__iterate_by_values(items=value["custom"], file=key, module=module, module_type="custom")

    def build_graph(
            self, 
            remove_from_root_path: Optional[str] = None, 
            import_type: Optional[str] = None
        ) -> None:

        if not remove_from_root_path:
            remove_from_root_path = self.remove_from_root_path
        
        if not import_type:
            import_type = self.import_type

        if import_type not in ["standard", "custom", "all"]:
            import_type = "all"

        if import_type == "all":
            collected_imports = list(self.__parse_imports_for_graph("custom", remove_from_root_path))
            collected_imports.extend(list(self.__parse_imports_for_graph("standard", remove_from_root_path)))
        else:
            collected_imports = list(self.__parse_imports_for_graph(import_type, remove_from_root_path))

        if collected_imports:
            self.graph_instance = self.graph_class(data=collected_imports, top_n_imports=self.top_n_imports)

    def display_graph_matrix(
            self,
            figure_size: Optional[Tuple[int, int]] = (15, 15),
            title: Optional[str] = "Adjacency Matrix",
            xlabel_tag: Optional[str] = "Imports",
            ylabel_tag: Optional[str] = "Paths",
            rotation: Optional[int] = 90,
            fontsize: Optional[int] = 8,
            cbar: Optional[bool] = True
    ) -> None:
        if not self.graph_instance:
            raise RuntimeError("You need to provide run build_graph() to create the graph first before displaying it.")
        
        self.graph_instance.display(
            figure_size=figure_size,
            img_title=title,
            xlabel_tag=xlabel_tag,
            ylabel_tag=ylabel_tag,
            rotation=rotation,
            fontsize=fontsize,
            cbar=cbar
        )

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
        cbar: Optional[bool] = False,
    ):
        if not self.graph_instance:
            raise RuntimeError("You need to provide run build_graph() to create the graph first before saving it.")
        
        self.graph_instance.save(
            figure_size=figure_size,
            img_title=img_title,
            file_name=file_name,
            xlabel_tag=xlabel_tag,
            ylabel_tag=ylabel_tag,
            rotation=rotation,
            fontsize=fontsize,
            cbar=cbar,
            local_save_path=local_save_path
        )
