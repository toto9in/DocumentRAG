from typing import List
from llama_index_client import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import VectorStoreIndex


class SimpleIndex:
    def __init__(self):
        self.splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=20,
        )

    def generate_index(self, documents: List[Document]) -> VectorStoreIndex:
        nodes = self.splitter.get_nodes_from_documents(documents)
        ## definir aq o storage_context para usar o PGVectorStore
        # vector_store = PGVectorStore.from_params(
        #     database=db_name,
        #     host=url.host,
        #     password=url.password,
        #     port=url.port,
        #     user=url.username,
        #     table_name="paul_graham_essay", ## criar um nome
        #     embed_dim=1536,  # openai embedding dimension
        # )
        ## storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(nodes=nodes)

        return index

    def get_index(table_name: str):
        # vector_store = PGVectorStore.from_params(
        #     database=db_name,
        #     host=url.host,
        #     password=url.password,
        #     port=url.port,
        #     user=url.username,
        #     table_name="paul_graham_essay", ## receber o table_name
        #     embed_dim=1536,  # openai embedding dimension
        # )
        ## index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
        return "hello"
