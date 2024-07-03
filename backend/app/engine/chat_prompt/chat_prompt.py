from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import ChatPromptTemplate
from llama_index.core.llms import ChatMessage
from llama_index.program.openai import OpenAIPydanticProgram
from llama_index.core.settings import Settings
from app.engine.chat_prompt.pydantic_prompt_models import (
    BasicInfo,
    MonetaryValuesAndContext,
)


class ChatPrompt:
    def __init__(self, documents):
        self.splitter = SentenceSplitter(
            chunk_size=2048,
            chunk_overlap=100,
        )
        self.documents = documents
        self.nodes = self.splitter.get_nodes_from_documents(documents)

    def get_cpnjs_and_names(self):
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
                        "Passagem do contrato: \n"
                        "------\n"
                        "{contract_info}\n"
                        "------"
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

        ## ver se isso vai sair formatado no responde do thunderclient
        top_output = program(contract_info=self.nodes[0].text)
        return top_output

    def get_monatary_values_with_context(self):
        prompt = ChatPromptTemplate(
            message_templates=[
                ChatMessage(
                    role="system",
                    content=(
                        "Você é um assistente especialista em extrair informacoes em R$ de um contrato, nao invente informacoes\n"
                        "LEMBRE-SE de retornar os dados extraidos apenas da passagem do contrato oferecida."
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        "Passagem do contrato: \n"
                        "------\n"
                        "{contract_info}\n"
                        "------"
                    ),
                ),
            ]
        )

        program = OpenAIPydanticProgram.from_defaults(
            output_cls=MonetaryValuesAndContext,
            llm=Settings.llm,
            prompt=prompt,
            verbose=True,
        )

        values = []

        for node in self.nodes:
            output = program(contract_info=node.text)
            values.append(output)

        return values
