from dotenv import load_dotenv

load_dotenv()

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
import os

from llama_parse import LlamaParse

Settings.chunk_size = 200

def llama_parse_parser():
    if os.getenv("LLAMA_CLOUD_API_KEY") is None:
        raise ValueError(
            "LLAMA_CLOUD_API_KEY environment variable is not set. "
            "Please set it in .env file or in your shell environment then run again!"
        )
    parser = LlamaParse(result_type="markdown", language="pt")
    return parser


## load the data from the directory, starter tutorial uses a .txt archive
reader = SimpleDirectoryReader(input_files=["contracts/8ea3b80e-2366-11ef-a2d5-c8cb9e66d08c.pdf"])
parser = llama_parse_parser()
reader.file_extractor = {".pdf": parser}
documents = reader.load_data()


# bge-base embedding model
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# ollama, using ollama to run llama3
Settings.llm = Ollama(model="llama3", request_timeout=360.0)

index = VectorStoreIndex.from_documents(
    documents, transformations=[SentenceSplitter(chunk_size=200)]
)

query_engine = index.as_query_engine()
response = query_engine.query("nome contratante")
print(response)