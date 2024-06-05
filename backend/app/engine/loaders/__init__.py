import logging
import yaml
from app.engine.loaders.file_parser import FileLoaderParserConfig, get_file_documents
from llama_index.core import VectorStoreIndex
from llama_index.core.settings import Settings

logger = logging.getLogger(__name__)


def load_config_file_parser():
    with open("config/file-parser.yaml") as f:
        config = yaml.safe_load(f)
    return config

def get_file_document(document_id: str):
    config = load_config_file_parser()
    documents = get_file_documents(document_id, FileLoaderParserConfig(**config['file']))
    ##index = VectorStoreIndex.from_documents(documents)
    ##query_engine = index.as_query_engine()
    ##response = query_engine.query("Extraia nomes, valores monetarios e cnpjs do contrato")
    from llama_index.core.node_parser import MarkdownElementNodeParser
    node_parser = MarkdownElementNodeParser(
        llm=Settings.llm, num_workers=8
    )

    nodes = node_parser.get_nodes_from_documents(documents)
    base_nodes, objects = node_parser.get_nodes_and_objects(nodes)
    recursive_index = VectorStoreIndex(nodes=base_nodes + objects)
    raw_index = VectorStoreIndex.from_documents(documents)

    from llama_index.postprocessor.flag_embedding_reranker import (
        FlagEmbeddingReranker,
    )

    reranker = FlagEmbeddingReranker(
        top_n=5,
        model="BAAI/bge-reranker-large",
    )      

    recursive_query_engine = recursive_index.as_query_engine(
        similarity_top_k=15, node_postprocessors=[reranker], verbose=True
    )

    raw_query_engine = raw_index.as_query_engine(
        similarity_top_k=15, node_postprocessors=[reranker]
    )

    response  = recursive_query_engine.query("Extraia o nome do contratante, o nome do/a contradada/o e o CNPJ do contratante em formato json")


    return response

