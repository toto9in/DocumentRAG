from llama_index.core.settings import Settings
import os


def init_settings():
    model_provider = os.getenv("MODEL_PROVIDER")
    if model_provider == "openai":
        pass
    elif model_provider == "ollama":
        init_ollama()
    elif model_provider == "anthropic":
        pass
    elif model_provider == "gemini":
        pass
    else:
        raise ValueError(f"Invalid model provider: {model_provider}")
    Settings.chunk_size = 200
    Settings.chunk_overlap = 20


def init_ollama():
    from llama_index.llms.ollama import Ollama
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding

    base_url = os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434"
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
    Settings.llm = Ollama(base_url=base_url, model=os.getenv("MODEL"), request_timeout=400)
