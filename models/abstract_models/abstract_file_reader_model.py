from abc import ABC, abstractmethod


class AbstractFileReaderModel(ABC):

    @abstractmethod
    def get_imports(self, file_path: str) -> str:
        pass
