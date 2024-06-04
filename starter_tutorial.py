from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter

Settings.chunk_size = 200

## load the data from the directory, starter tutorial uses a .txt archive
documents = SimpleDirectoryReader("data_starter_tutorial").load_data()

# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama, using ollama to run llama3
Settings.llm = Ollama(model="llama3", request_timeout=360.0)

index = VectorStoreIndex.from_documents(
    documents, transformations=[SentenceSplitter(chunk_size=200)]
)

query_engine = index.as_query_engine()
response = query_engine.query("CNPJ")
print(response)