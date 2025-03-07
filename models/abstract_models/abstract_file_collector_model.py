from typing import List
from pathlib import Path
from abc import ABC, abstractmethod


class AbstractFileCollectorModel(ABC):

    @abstractmethod
    def collect_files(
            self, 
            root_path: str | Path = None, 
            extension: str = None, 
            exclude_start_characters: str =  None,
            exclude_end_characters: str =  None,
            return_files: bool = False
            ) -> List[str]:
        pass
