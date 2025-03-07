from typing import List
from pathlib import Path
from pydantic import BaseModel, Field
from ast import parse, Import, ImportFrom
from .abstract_models.abstract_file_reader_model import AbstractFileReaderModel


class FileReaderModel(BaseModel, AbstractFileReaderModel):
    line_separator: str = Field(default="\n")
    file_path: str | Path = Field(min_length=1)
    file_imports: List[str] = Field(default_factory=list)
    import_tags: List[str] = Field(default_factory=lambda: ["import", "from"])

    def __is_import_statement(self, line: str) -> bool:
        try:
            tree = parse(line)
            return isinstance(tree.body[0], Import) or isinstance(tree.body[0], ImportFrom)
        except (SyntaxError, IndexError):
            return False

    def __extract_content(self) -> str:
        try:
            with open(self.file_path, 'rb') as file:
                content = file.read().decode('utf-8')
                return content
        except FileNotFoundError:
            return ""

    def __extract_imports(self) -> List[str]:
        lines = self.__extract_content().split(self.line_separator)
        return [
            line.split(" as ")[0].strip() if "as" in line else line.strip()
            for line in lines if self.__is_import_statement(line.strip())
        ]

    def get_imports(self) -> List[str | None]:
        self.file_imports = self.__extract_imports()
        return self.file_imports
