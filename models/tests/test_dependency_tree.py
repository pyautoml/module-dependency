import pytest
from pathlib import Path
from ..graph_model import GraphModel
from ..import_model import ImportModel
from ..dependency_model import DependencyModel
from ..file_reader_model import FileReaderModel
from ..file_collector_model import FileCollectorModel

class MockGraphModel(GraphModel):
    pass

class MockImportModel(ImportModel):
    def get_libraries(self, as_json=False):
        return {"standard": ["os"], "custom": ["custom_module"]}

class MockFileReaderModel(FileReaderModel):
    def get_imports(self):
        return ["os", "custom_module"]

class MockFileCollectorModel(FileCollectorModel):
    def collect_files(
            self, 
            root_path: str | Path = None, 
            extension: str = None, 
            exclude_start_characters: str =  None,
            exclude_end_characters: str =  None,
            return_files: bool = False
            ) -> list[str]:
        return ['file1.py', 'file2.py']

@pytest.fixture
def mock_graph_class():
    return MockGraphModel

@pytest.fixture
def mock_file_collector():
    return MockFileCollectorModel()

@pytest.fixture
def mock_file_import_class():
    return MockImportModel

@pytest.fixture
def mock_file_reader_class():
    return MockFileReaderModel

@pytest.fixture
def dependency_model(mock_graph_class, mock_file_collector, mock_file_import_class, mock_file_reader_class):
    return DependencyModel(
        graph_class=mock_graph_class,
        file_collector=mock_file_collector,
        file_import_class=mock_file_import_class,
        file_reader_class=mock_file_reader_class,
        root_directory='root/some_directory/'
    )

def test_initialization_and_run(dependency_model):
    dependency_model._DependencyModel__run()
    assert 'file1.py' in dependency_model.imports
    assert 'file2.py' in dependency_model.imports


def test_path_to_posix(dependency_model):
    posix_path = dependency_model._DependencyModel__path_to_posix('C:\\path\\to\\file')
    assert posix_path == 'C:/path/to/file'


def test_filter_by_path(dependency_model):
    dependency_model.imports = {'file1.py': {'standard': [], 'custom': []}}
    filtered_imports = dependency_model._DependencyModel__filter_by_path('file1.py')
    assert filtered_imports == {'standard': [], 'custom': []}


def test_save_graph_matrix(dependency_model, tmp_path):
    dependency_model.graph_instance = GraphModel(data=[
        {'file': 'file1.py', 'import': 'os'},
        {'file': 'file2.py', 'import': 'sys'}
    ])
    file_path = tmp_path / "test_graph.png"
    try:
        dependency_model.save_graph_matrix(file_name=str(file_path), local_save_path=f"{Path.cwd().as_posix()}/files")
    except RuntimeError:
        pytest.fail("save_graph_matrix() raised RuntimeError unexpectedly!")
    assert file_path.exists()
