import re
import sys
from importlib import metadata
from typing import List, Tuple
from functools import lru_cache
from pkgutil import iter_modules


_REMOVE_KEYROWDS: List[str] = [
    "as",
    "from",
    "import",
]

@lru_cache(maxsize=128)
def module_in_metadata(module_name: str) -> bool:
    try:
        data = metadata.metadata(module_name).get("Name") == "Python"
        return data
    except metadata.PackageNotFoundError:
        return False

@lru_cache(maxsize=128)
def module_in_iters(module_name: str) -> bool:
    return module_name in {name for _, name, _ in iter_modules()}

@lru_cache(maxsize=128)
def module_in_builtins(module_name: str) -> bool:
    return module_name in sys.builtin_module_names

@lru_cache(maxsize=128)
def module_is_standard_library(module_name: str) -> bool:
    in_metadata: bool = module_in_metadata(module_name)
    in_builtins: bool = module_in_builtins(module_name)
    in_iter_modules: bool = module_in_iters(module_name)
    return any([in_metadata, in_builtins, in_iter_modules])
    

def _remove_renamed_imports(import_string: str) -> str:
    """Remove renamed imports from string. Example: 'import pandas as pd' will remove ' as pd' from the string."""
    if not import_string:
        raise ValueError("import_string cannot be None or empty")
    if not isinstance(import_string, str):
        raise TypeError(f"import_string should be str, not {type(import_string).__name__}")
    return re.sub(r'\s+as\s.*', '', import_string)


def _remove_keywords(import_string: str) -> str:
    """Remove unwanted keywords from string. Example: 'from os import path' will remove 'from' and 'import' from the string."""  
    import_string: str = _remove_renamed_imports(import_string)
    import_string: List[str] = [item for item in import_string.split(" ") if item.lower() not in _REMOVE_KEYROWDS]   
    return ' '.join([x for x in import_string if x and x != ''])


def root_cleanup(root: str) -> str:
    root: str = str(root).replace("from ", "")
    root: str = root.replace(" ", "").replace("..", "")
    root: str = root.strip()

    if root.startswith("."):
        root: str = root.replace(".", "", 1)
    return root

def module_name_cleanup(module_name: str) -> str:
    if module_name.startswith(".."):
        module_name: str = str(module_name.replace("..", "", 1).split(".")[0])
   
    if module_name.startswith("."):
        module_name: str = str(module_name.replace(".", "", 1).split(".")[0])
    
    return module_name

def find_imports(data: str):

    if "import " in data:
        data = _remove_renamed_imports(data)
        data = data.split("import ")[1]
        data = [data.replace(" ", "")]
    return data

@lru_cache(maxsize=128)        
def classify_module(module_name: str) -> bool:
    """
    When a library starts with '.' or '..' it is assumed to be a custom module.
    
    [Tricky part]
    Some libraries are builtins or python's native libs. They have a dot '.' like in 'import matplotlib.pyplot' and in such case,
    root should be checked from left to right.
    """
    module_name: str = _remove_keywords(module_name)
    module_name: str = module_name_cleanup(module_name)

    if "." in module_name:
        elements: List[str] = module_name.split(".")
        for element in elements:
            if not element or element == '':
                try:
                    elements.remove(element)
                except:
                    pass
        if module_is_standard_library(elements[0]):
            return True
        return False
    return module_is_standard_library(module_name)


def __split_into_module_and_imports(data: str) -> List[str]:
    item = data.rsplit("import ", 1)
    if item[0] == '' or not item[0]:
        item[0] = item[1]
    return item[0]
    

@lru_cache(maxsize=128)   
def find_root(data: str) -> Tuple[str, bool]:
    item = __split_into_module_and_imports(data)
    root_in_standard_lib: bool = classify_module(item)
    root: str = root_cleanup(item)
    return root, root_in_standard_lib
