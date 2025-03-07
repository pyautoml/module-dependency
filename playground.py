from models.graph_model import GraphModel
from models.import_model import ImportModel
from models.file_reader_model import FileReaderModel
from models.dependency_model import DependencyModel
from models.file_collector_model import FileCollectorModel


def play():

    imports_type: str = "all"  # standard, custom, all

    dependency_collector = DependencyModel(
        # top_n_imports=0,                                          # [Optional] X/Y axis elements display limit
        graph_class=GraphModel,                                    
        file_import_class=ImportModel,                             
        file_reader_class=FileReaderModel,                          
        file_collector=FileCollectorModel(),                        
        exclude_start_characters="__",                              # [Optional] exclude files starting with particular characters
        # exclude_end_characters="__",                              # [Optional] exclude files ending with particular characters
        import_type=imports_type,                                   # [Optional] options: custom, standard, all 
        # remove_from_root_path="",                                 # [Optional] shorted the path on the displayed matrix PNG, e.g.: "C:/Users/.../Desktop/"
        autobuild=True,                                             # [Optional] can be skipped, but the it obligatory to build it by invoking build_graph()
    )

    dependency_collector.save_graph_matrix(
        figure_size=(15, 8),
        file_name=f"{imports_type}_imports",                        
        img_title="Adjacency Matrix",       
        local_save_path=""                                          # [Oblicatory] If you want to save a file locally, a full path must be provided (Path or str)               
    )
