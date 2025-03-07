from abc import ABC, abstractmethod


class AbstractGraphModel(ABC):

    @abstractmethod
    def display(self) -> None:
        pass

    @abstractmethod
    def save(self, local_save_path: str = None) -> None:
        pass
