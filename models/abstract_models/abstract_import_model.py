from typing import Optional
from abc import ABC, abstractmethod


class AbstractImportModel(ABC):

    @abstractmethod
    def extract(self):
        pass

    @abstractmethod
    def get_libraries(self, as_json: Optional[bool] = False, indent: Optional[int] =  4) -> dict:
        pass
