import pytest
from ..imports import (
    find_root,
    root_cleanup,
    module_in_iters,
    classify_module,
    _remove_keywords,
    module_in_metadata, 
    module_in_builtins, 
    _remove_renamed_imports,
    module_is_standard_library,
)


@pytest.mark.parametrize('import_string, root, root_in_standard_lib', [
    ('from pathlib import Path', 'pathlib', True),
    ('from some.custom.model import dummy', 'some.custom.model', False),
    ('from ..abstract_models.abstract_graph_model import dummy', 'abstract_models.abstract_graph_model', False),
    ('from .abstract_models.abstract_file_collector_model import dummy', 'abstract_models.abstract_file_collector_model', False),
])
def test_find_custom_root(import_string, root, root_in_standard_lib):
    output = find_root(import_string)
    assert output[0] == root and output[1] == root_in_standard_lib


@pytest.mark.parametrize('root, expected', [
    ('from ..some.custom.model ', 'some.custom.model'),
    ('from ..abstract_models.abstract_graph_model', 'abstract_models.abstract_graph_model'),
    ('.abstract_models.abstract_file_collector_model', 'abstract_models.abstract_file_collector_model'),
])
def test_clean_root(root, expected):
    assert root_cleanup(root) == expected

def _test_module_in_metadata():

    model_1: str = "os"
    model_2: str = "numpy"
    model_3: str = "pytest"
    model_4: str = "networkx"
    model_5: str = "itertools"

    assert not module_in_metadata(model_1)
    assert not module_in_metadata(model_2)
    assert not module_in_metadata(model_3)
    assert not module_in_metadata(model_4)
    assert not module_in_metadata(model_5)


def _test_module_in_iters():

    model_1: str = "gc"
    model_2: str = "os"
    model_3: str = "numpy"
    model_4: str = "pytest"
    model_5: str = "networkx"
    model_6: str = "itertools"
    model_7: str = "functools"
    model_8: str = "custom_import"

    assert not module_in_iters(model_1)
    assert module_in_iters(model_2)
    assert module_in_iters(model_3)
    assert module_in_iters(model_4)
    assert module_in_iters(model_5)
    assert not module_in_iters(model_6)
    assert module_in_iters(model_7)
    assert not module_in_iters(model_8)


def _test_module_in_builtins():
    
    model_1: str = "gc"
    model_2: str = "os"
    model_3: str = "numpy"
    model_4: str = "pytest"
    model_5: str = "networkx"
    model_6: str = "itertools"
    model_7: str = "functools"
    model_8: str = "custom_import"

    assert module_in_builtins(model_1)
    assert not module_in_builtins(model_2)
    assert not module_in_builtins(model_3)
    assert not module_in_builtins(model_4)
    assert not module_in_builtins(model_5)
    assert  module_in_builtins(model_6)
    assert not module_in_builtins(model_7)
    assert not module_in_builtins(model_8)


def _test_module_is_standard_library():
    
    model_1: str = "gc"
    model_2: str = "os"
    model_3: str = "numpy"
    model_4: str = "pytest"
    model_5: str = "networkx"
    model_6: str = "itertools"
    model_7: str = "functools"
    model_8: str = "custom_library"

    assert module_is_standard_library(model_1)
    assert module_is_standard_library(model_2)
    assert module_is_standard_library(model_3)
    assert module_is_standard_library(model_4)
    assert module_is_standard_library(model_5)
    assert module_is_standard_library(model_6)
    assert module_is_standard_library(model_7)
    assert not module_is_standard_library(model_8)


def _test_remove_renamed_imports():

    string_1: str = "import data as ddd"
    string_2: str = "import ast"
    string_3: str = "from pydantic import nothing as nn"
    string_4: None = None
    string_5: int = 10
    string_6: dict = {"data": "hello"}

    assert _remove_renamed_imports(string_1) == "import data"
    assert _remove_renamed_imports(string_2) == "import ast"
    assert _remove_renamed_imports(string_3) == "from pydantic import nothing"

    with pytest.raises(ValueError) as excinfo:
        assert _remove_renamed_imports(string_4) == "from pydantic import nothing"
    assert excinfo.match("import_string cannot be None or empty")

    with pytest.raises(TypeError) as excinfo:
        assert _remove_renamed_imports(string_5) == "from pydantic import nothing"
    assert excinfo.match("import_string should be str, not int")

    with pytest.raises(TypeError) as excinfo:
        assert _remove_renamed_imports(string_6) == "from pydantic import nothing"
    assert excinfo.match("import_string should be str, not dict")


def _test_remove_keywords():
    
    string_1: str = "import data as ddd"
    string_2: str = "import ast"
    string_3: str = "from pydantic import nothing as nn"
    string_4: None = None
    string_5: int = 10
    string_6: dict = {"data": "hello"}

    assert _remove_keywords(string_1) == "data"
    assert _remove_keywords(string_2) == "ast"
    assert _remove_keywords(string_3) == "pydantic nothing"

    with pytest.raises(ValueError) as excinfo:
        assert _remove_keywords(string_4) == "from pydantic import nothing"
    assert excinfo.match("import_string cannot be None or empty")

    with pytest.raises(TypeError) as excinfo:
        assert _remove_keywords(string_5) == "from pydantic import nothing"
    assert excinfo.match("import_string should be str, not int")

    with pytest.raises(TypeError) as excinfo:
        assert _remove_keywords(string_6) == "from pydantic import nothing"
    assert excinfo.match("import_string should be str, not dict")


def _test_classify_module():
    
    string_1: str = "import data as ddd"
    string_2: str = "import ast"
    string_3: str = "from pydantic import nothing as nn"
    string_4: str = "from ..graph_model import GraphModel"
    string_5: str = "from .dependency_model import DependencyModel"
    string_6: str = "import typing"
    string_7: str = "from typing"
    string_8: None = None
    string_9: int = 10
    string_10: dict = {"data": "hello"}

    assert not classify_module(string_1)
    assert classify_module(string_2)
    assert not classify_module(string_3)
    assert not classify_module(string_4)
    assert not classify_module(string_5)
    assert classify_module(string_6)
    assert classify_module(string_7)

    with pytest.raises(ValueError) as excinfo:
        assert classify_module(string_8)
    assert excinfo.match("import_string cannot be None or empty")

    with pytest.raises(TypeError) as excinfo:
        assert classify_module(string_9)
    assert excinfo.match("import_string should be str, not int")

    with pytest.raises((TypeError, AssertionError)) as excinfo:
        assert classify_module(string_10)
    assert excinfo.match("unhashable type: 'dict'") or excinfo.match("Regex pattern did not match.")
