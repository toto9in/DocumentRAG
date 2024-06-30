from typing import List
from llama_index_client import Document
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import StorageContext, VectorStoreIndex
from chromadb.api import ClientAPI
from llama_index.vector_stores.chroma import ChromaVectorStore
import uuid


class SimpleIndex:
    def __init__(self):
        self.splitter = SentenceSplitter(
            chunk_size=1024,
            chunk_overlap=20,
        )

    def generate_index(self, documents: List[Document], chroma_client: ClientAPI):
        nodes = self.splitter.get_nodes_from_documents(documents)
        simple_index_collection_id = uuid.uuid1()
        chroma_collection = chroma_client.get_or_create_collection(
            simple_index_collection_id
        )
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex(
            storage_context=storage_context,
            nodes=nodes,
        )

        return (index, simple_index_collection_id)

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
