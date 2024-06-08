import logging
import yaml
from app.engine.loaders.file_parser import FileLoaderParserConfig, get_file_documents
from llama_index.core import VectorStoreIndex
from llama_index.core.settings import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.postprocessor.flag_embedding_reranker import (
    FlagEmbeddingReranker,
)

logger = logging.getLogger(__name__)


def load_config_file_parser():
    with open("config/file-parser.yaml") as f:
        config = yaml.safe_load(f)
    return config

## isso aq tambem nao esta implementado 100%, nao eh pra ele retornar uma query, aq eh so exemplo pq tava testando, tem que reformular
def get_file_document(document_id: str):
    config = load_config_file_parser()

    documents = get_file_documents(document_id, FileLoaderParserConfig(**config['file']))

    splitter = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=20,
    )
    nodes = splitter.get_nodes_from_documents(documents)
    index_from_document = VectorStoreIndex(nodes=nodes)

    reranker = FlagEmbeddingReranker(
        top_n=5,
        model="BAAI/bge-reranker-large",
    )   

    simple_query = index_from_document.as_query_engine(
        similarity_top_k=15, node_postprocessors=[reranker]
    )

    query = "O que a Clausula 1 do contrato fala?"

    response = simple_query.query(query)

    return response

## refatorar isso aq pelo amor de deus, foi so exemplo
def get_basic_info(document_id: str):
    config = load_config_file_parser()

    documents = get_file_documents(document_id, FileLoaderParserConfig(**config['file']))

    splitter = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=20,
    )
    nodes = splitter.get_nodes_from_documents(documents)

    from pydantic import BaseModel, Field
    from llama_index.program.openai import OpenAIPydanticProgram
    from llama_index.core import ChatPromptTemplate
    from llama_index.core.llms import ChatMessage
    from llama_index.llms.openai import OpenAI

    class BasicInfo(BaseModel):
        """Data model for basic  extracted information."""

        nome_contratante: str = Field(
            description="Nome do contrante", default='0'
        )
        cnpj_contratante: str = Field(
            description="CNPJ do contratante", default='0'
        )
        nome_contratado: str = Field(description="Nome do contratado/a", default='0')
        cnpj_contratado: str = Field(description="CNPJ do contratado/a", default='0')



    prompt = ChatPromptTemplate(
        message_templates=[
            ChatMessage(
                role="system",
                content=(
                    "Você é um especialista em extrair informações de um contrato como: nome do contratante, nome do contratado/a, CPNJ do contratante e o CNPJ do contratado/a. \n"
                    "Você extrai esses dados e retorna em formato JSON, de acordo com o schema JSON oferecido, de uma passagem do contrato. \n"
                    "LEMBRE-SE de retornar os dados extraidos apenas da passagem do contrato oferecida."
                ),
            ),
            ChatMessage(
                role="user",
                content=(
                    "Passagem do contrato: \n" "------\n" "{contract_info}\n" "------"
                ),
            ),
        ]
    )

    program = OpenAIPydanticProgram.from_defaults(
        output_cls=BasicInfo,
        llm=Settings.llm,
        prompt=prompt,
        verbose=True,
    )

    output = program(contract_info=nodes[0].text)
    print("Output JSON From pdf File: ")
    print(output.model_dump_json(indent=2))
    return (output)
   

