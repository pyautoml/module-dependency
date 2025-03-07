from json import dumps
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional
from utilities.imports import find_root, find_imports
from .abstract_models.abstract_import_model import AbstractImportModel


class ImportModel(BaseModel, AbstractImportModel):
    imports: List[str] = Field(default_factory=list)
    custom_libraries: dict = Field(default_factory=dict)
    standard_libraries: dict = Field(default_factory=dict)

    def __init__(self, *args, **data):
        super().__init__(*args, **data)
        self.extract()

    def __hash__(self):
        return super().__hash__()
    
    def __choose_library_type(self, is_standard: bool) -> dict:
        return self.standard_libraries if is_standard else self.custom_libraries

    def __process_module(self, data: str) -> Tuple[str, List[str|None], bool]:
        root, is_root_standard_library = find_root(data)
        imported: List[str] = find_imports(data)
        return root, imported, is_root_standard_library
    
    def __imports_from_add_to_library(
        self, is_standard_library: bool, root: str, imported: List[str]
    ):
        library_type = self.__choose_library_type(is_standard_library)
        if not imported:
            return 
        
        for library in imported:
            if "," in library:
                library = library.split(",")
                library = [str(i.strip()).replace(" ", "") for i in library]
            else:
                library = library.strip()

            if root not in library_type.keys():
                if isinstance(library, list):
                    if len(library) > 1:
                        library_type[root] = []
                        for lib in library:
                            library_type[root].append(lib)
                    else:
                        library_type[root] = [library]
                elif isinstance(library, str):
                    library_type[root] = [library]
            else:
                library_type[root].append(library)
    

    def __import_full_add_to_library(self, library_type: bool, root: str):
        library: dict = self.__choose_library_type(library_type)

        if "," in root:
            roots = root.split(",")
            for root in roots:
                root = root.strip().replace(" ", "")
                if root not in library.keys():
                    library[root] = []
        else:
            if root not in library.keys():
                library[root] = []

    def extract(self):
        if not self.imports:
            return
        
        if isinstance(self.imports, str):
            self.imports: list = [self.imports]

        for item in self.imports:
            root, imported, is_root_standard_library = self.__process_module(item)
            if "from" in item:
                self.__imports_from_add_to_library(
                    root=root, imported=imported, is_standard_library=is_root_standard_library
                )
            else:
                self.__import_full_add_to_library(
                    root=root, library_type=is_root_standard_library
                )

    def get_libraries(self, as_json: Optional[bool] = False, indent: Optional[int] =  4) -> dict:
        data = {"custom": self.custom_libraries, "standard": self.standard_libraries}
        return dumps(data, indent=indent) if as_json else data
