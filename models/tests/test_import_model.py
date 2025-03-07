import pytest
from typing import List
from ..import_model import ImportModel

@pytest.fixture
def paths() -> List[str]:
    return [
        'path/to_external/file1.txt',
        'path/to/dummy.py',

        'project/frontend/styles.css',
        'repo/project_1/__init__.py',
        'repo/project/deprecated/do_not_use.c',
    ]

@pytest.fixture
def import_model() -> ImportModel:
    return ImportModel()


def test_initialization_and_extraction():
    imports = [
        "from os import path",
        "import pandas",
        "from custom_module import custom_function",
        "import custom_library"
    ]
    import_model = ImportModel(imports=imports)
    
    assert "os" in import_model.standard_libraries
    assert "pandas" in import_model.standard_libraries
    assert "custom_module" in import_model.custom_libraries
    assert "custom_library" in import_model.custom_libraries


@pytest.mark.parametrize("module, root, imported, is_root_standard_library", [
    ("import os", "os", ["os"], True),
    ("from my.library import AbstractDummy", "my.library", ["AbstractDummy"], False),
    ("pandas", "pandas", "pandas", True),
    ("from weird_one import nothing", "weird_one", ["nothing"], False),
])
def test_is_import_standard(import_model, module, root, imported, is_root_standard_library):
    data = import_model._ImportModel__process_module(module)
    assert data[0] == root
    assert data[1] == imported
    assert data[2] == is_root_standard_library


def _test_get_libraries():
    import_model = ImportModel()
    import_model.__setattr__("custom_libraries", {"custom": ["awesome!", "great!"]})
    import_model.__setattr__("standard_libraries", {"standard": ["os", "pandas"]})
    libraries = import_model.get_libraries()
    assert libraries == {
        "custom": {"custom": ["awesome!", "great!"]},
        "standard": {"standard": ["os", "pandas"]}
    }

def _test_get_libraries_as_json():
    import_model = ImportModel()
    import_model.__setattr__("custom_libraries", {"custom": ["awesome!", "great!"]})
    import_model.__setattr__("standard_libraries", {"standard": ["os", "pandas"]})
    libraries = import_model.get_libraries(as_json=True, indent=0)
    expected: str = """{\n"custom": {\n"custom": [\n"awesome!",\n"great!"\n]\n},\n"standard": {\n"standard": [\n"os",\n"pandas"\n]\n}\n}"""
    assert libraries == expected


def test_imports_from():
    import_model = ImportModel()
    import_model.imports = [
        "import os", 
        "from itertools import islice",
        "from .abstract_models.abstract_graph_model import AbstractGraphModel"
    ]
    import_model.extract()

    assert "os" in import_model.standard_libraries
    assert "itertools" in import_model.standard_libraries
    assert "abstract_models.abstract_graph_model" in import_model.custom_libraries

    assert len(import_model.custom_libraries) == 1
    assert len(import_model.standard_libraries) == 2
