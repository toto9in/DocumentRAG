# from dotenv import load_dotenv
# from pydantic import BaseModel, Field

# load_dotenv()

# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings, SummaryIndex
# from llama_index.embeddings.huggingface import HuggingFaceEmbedding
# from llama_index.llms.ollama import Ollama
# from llama_index.core import Settings
# from llama_index.core.node_parser import SentenceSplitter
# import os
# from llama_index.core.prompts import PromptTemplate


# from llama_parse import LlamaParse


# class JsonResponse(BaseModel):
#     nome_contratante: str = Field(description="Nome do contratante")
#     cnpj_contratante: str = Field(description="CNPJ do contratante")
#     nome_contratado: str = Field(description="Nome do contratado")
#     cnpj_contratado: str = Field(description="CNPJ do contratado")


# def llama_parse_parser():
#     if os.getenv("LLAMA_CLOUD_API_KEY") is None:
#         raise ValueError(
#             "LLAMA_CLOUD_API_KEY environment variable is not set. "
#             "Please set it in .env file or in your shell environment then run again!"
#         )
#     parser = LlamaParse(result_type="markdown", language="pt")
#     return parser


# ## load the data from the directory, starter tutorial uses a .txt archive
# reader = SimpleDirectoryReader(input_files=["contracts/8ea3b80e-2366-11ef-a2d5-c8cb9e66d08c.pdf"])
# parser = llama_parse_parser()
# reader.file_extractor = {".pdf": parser}
# documents = reader.load_data()


# # bge-base embedding model
# Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")

# # ollama, using ollama to run llama3
# llm = Ollama(model="llama3", request_timeout=360.0)
# Settings.llm = llm

# index = SummaryIndex.from_documents(
#     documents, transformations=[SentenceSplitter(chunk_size=1024)]
# )

# print(documents[0].text[:2000])
# prompt_tmpl = PromptTemplate("O texto de exemplo eh um contrato, extraia dele o nome do contratante que está no contrato, o nome do contratado/a que está no contrato, o CNPJ do contratante e o CNPJ do contratado {text}")
# response = llm.structured_predict(JsonResponse, prompt_tmpl, text=documents[0].text[:2000])
# print(response)

# query_engine = index.as_query_engine(response_mode="tree_summarize")
# response = query_engine.query("O que diz a cláusula 1 do contrato?")
# print(response)


import enum


class EInsuranceTypesId(enum.Enum):
    seguro_garantia_para_execucao_de_contratos = 1
    seguro_garantia_para_licitacoes = 2
    seguro_garantia_para_loteamentos = 3
    seguro_garantia_para_retencao_de_pagamento = 4
    seguro_garantia_para_processos_judiciais = 5
    seguro_de_vida_em_grupo = 6
    seguro_de_riscos_de_engenharia = 7
    seguro_de_responsabilidade_civil = 8


def get_insurance_type_id(insurance_types: str):
    insurance_types = insurance_types.split(",")
    print(insurance_types)
    insurance_types_id = []
    for insurance_type in insurance_types:
        insurance_types_id.append(int(insurance_type))
    return insurance_types_id


insurance_types = get_insurance_type_id("1, 7, 8")
print(insurance_types)
