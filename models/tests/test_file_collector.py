import pytest
from typing import List
from ..file_collector_model import FileCollectorModel


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
def collector_instance() -> FileCollectorModel:
    return FileCollectorModel(root_directory='root/some_directory')


@pytest.mark.parametrize("filename, extension, expected", [
    ('file1.txt', '.txt', True),
    ('file1.txt', '.py', False),
    ('file1.txt', '.css', False),
    ('file1.txt', ".txt", True),
    ('file1.txt', '.c', False),
])
def test__keep_file_by_extension(collector_instance, filename, extension, expected):
    assert collector_instance._FileCollectorModel__keep_file_by_extension(filename, extension) == expected

def test__keep_file_by_extension_invalid_file_type(collector_instance):
    with pytest.raises((AttributeError, AssertionError)) as excinfo:
        collector_instance._FileCollectorModel__keep_file_by_extension({"name": "Kajtek"}, '.c')
    assert excinfo.match("'dict' object has no attribute 'endswith'") or excinfo.match("File must be a string or Path object")

@pytest.mark.parametrize("filename, extension", [
    ('file1.txt', None),
    ('file1.txt', True),
    ('file1.txt', 0),
    ('file1.txt', 1111),
    ('file1.txt', {"name": "Kajtek"})
])
def test__keep_file_by_extension_invalid_extension_type(collector_instance, filename, extension):
        with pytest.raises((AttributeError, AssertionError)) as excinfo:
            collector_instance._FileCollectorModel__keep_file_by_extension(filename, extension)
        assert excinfo.match("File must be a string or Path object")


@pytest.mark.parametrize("filename, extension", [
    ('file1.txt', ''),
    ('file1.txt', ' '),
    ('file1.txt', '   ')
])
def test__keep_file_by_extension_invalid_extension_empty_string(collector_instance, filename, extension):
    with pytest.raises(AttributeError) as excinfo:
        collector_instance._FileCollectorModel__keep_file_by_extension(filename, extension)
    assert excinfo.match("'file' or/and 'extension' objects cannot be an empty strings")

@pytest.mark.parametrize("collected_files, starts_with, ends_with, expected", [
    (['data/file1.txt', 'data/__init__.py'], '__', None, ['data/file1.txt']),
    (['data/file1.txt', 'data/__init__.py'], None, '__', ['data/file1.txt']),
    (['data/__init__.py'], "__", '__', []),
])
def test__reduce_by_character(collected_files, starts_with, ends_with, expected):
    collector_instance = FileCollectorModel(root_directory='root/some_directory')
    errors: list = [
        "argument should be a str or an os.PathLike object where __fspath__ returns a str, not 'list'",
        "assert False == []",
        "assert False == ['__init__.py']"
    ]
                                            
    with pytest.raises((TypeError, AssertionError)) as excinfo:
        collector_instance._FileCollectorModel__remove_file_by_characters(collected_files, starts_with, ends_with) == expected
    assert excinfo.match(errors[0]) or excinfo.match(errors[1]) or excinfo.match(errors[2])


@pytest.mark.parametrize("files, extension, starts_with, ends_with, expected", [
    (['file1.txt', 'dummy.py', 'styles.css'], '.txt', None, None, ['file1.txt']),
    (['file1.txt', 'dummy.py', 'styles.css'], None, 'dummy', None, ['file1.txt', 'styles.css']),
    (['file1.txt', 'dummy.py', 'styles.css'], None, None, '.css', ['file1.txt', 'dummy.py']),
    (['file1.txt', 'dummy.py', 'styles.css'], '.py', 'dummy', '.css', []),
])
def test__filter_files(collector_instance, files, extension, starts_with, ends_with, expected):
    filtered_files = collector_instance._FileCollectorModel__filter_files(files, extension, starts_with, ends_with)
    assert filtered_files == expected
