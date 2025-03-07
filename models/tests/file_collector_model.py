from os import walk
from pathlib import Path
from typing import Optional, List
from pydantic import BaseModel, Field
from .abstract_models.abstract_file_collector_model import AbstractFileCollectorModel


class FileCollectorModel(BaseModel, AbstractFileCollectorModel):
    files: List[str] = Field(default_factory=list)

    def __keep_file_by_extension(self, file: str, extension: str) -> bool:
        
        if not isinstance(file, str):
            raise AttributeError("'dict' object has no attribute 'endswith'")
        
        if not isinstance(extension, str):
            raise AssertionError("File must be a string or Path object")
        
        if file.replace(" ", "") == "" or extension.replace(" ", "") == "":
            raise AttributeError("'file' or/and 'extension' objects cannot be an empty strings")
        
        return file.endswith(extension)

    def __remove_file_by_characters(
            self, 
            path: str, 
            starts_with: Optional[str] = None, 
            ends_with: Optional[str] = None
        ) -> bool:
        
        file = Path(path).name
        if starts_with and file.startswith(starts_with):
            return False
        if ends_with and file.endswith(ends_with):
            return False
        return True

    def __filter_files(self, files: List[str], extension: Optional[str], starts_with: Optional[str], ends_with: Optional[str]) -> List[str]:
        return [
            file for file in files
            if (not extension or self.__keep_file_by_extension(file, extension)) and
               self.__remove_file_by_characters(file, starts_with, ends_with)
        ]

    def collect_files(
            self,
            root_path: str | Path,
            extension: Optional[str] = None,
            exclude_start_characters: Optional[str] = None,
            exclude_end_characters: Optional[str] = None,
            return_files: Optional[bool] = False
        ) -> List[str]:

        collected_files = [
            str(Path(root) / file).replace("\\", "/")
            for root, _, files in walk(root_path)
            for file in files
        ]

        collected_files = self.__filter_files(
            collected_files, 
            extension, 
            exclude_start_characters, 
            exclude_end_characters
        )

        if return_files:
            return list(set(collected_files))
        self.files = list(set(collected_files))
        return self.files
