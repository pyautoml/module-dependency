import pytest
from numpy import array
from pathlib import Path
from networkx import DiGraph
from ..graph_model import GraphModel

@pytest.fixture
def graph_data():
    return [
        {'file': 'file1.py', 'import': 'module1'},
        {'file': 'file2.py', 'import': ['module2', 'module3']},
        {'file': 'file3.py', 'import': 'module4'}
    ]

@pytest.fixture
def graph_instance(graph_data) -> GraphModel:
    return GraphModel(data=graph_data)

def test_initialization_and_build(graph_instance):
    assert isinstance(graph_instance.graph, DiGraph)
    assert graph_instance.is_built
    assert 'file1.py' in graph_instance.nodes
    assert 'module1' in graph_instance.nodes
    assert ('file1.py', 'module1') in graph_instance.edges

def test_get_nodes(graph_instance):
    nodes = graph_instance._GraphModel__get_nodes()
    assert 'file1.py' in nodes
    assert 'module1' in nodes

def test_get_edges(graph_instance):
    edges = graph_instance._GraphModel__get_edges()
    assert ('file1.py', 'module1') in edges
    assert ('file2.py', 'module2') in edges
    assert ('file2.py', 'module3') in edges

def test_to_custom_adjacency_matrix(graph_instance):
    matrix, paths, imports = graph_instance._GraphModel__to_custom_adjacency_matrix()
    expected_matrix = array([
        [1, 0, 0, 0],
        [0, 1, 1, 0],
        [0, 0, 0, 1]
    ])
    assert (matrix == expected_matrix).all()
    assert paths == ['file1.py', 'file2.py', 'file3.py']
    assert imports == ['module1', 'module2', 'module3', 'module4']


def test_save(graph_instance, tmp_path):
    # Assuming save method works correctly if no exception is raised
    file_path = tmp_path / "test_graph.png"
    try:
        graph_instance.save(local_save_path=f"{Path.cwd().as_posix()}/files", file_name=str(file_path))
    except RuntimeError:
        pytest.fail("save() raised RuntimeError unexpectedly!")
    assert file_path.exists()

def test_list_edges(graph_instance):
    edge_list = graph_instance.list_edges()
    assert not edge_list.empty
    assert 'source' in edge_list.columns
    assert 'target' in edge_list.columns
    assert ('file1.py', 'module1') in edge_list.values
