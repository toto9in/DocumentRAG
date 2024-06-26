from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Path, UploadFile
from sqlalchemy.orm import Session
from app.engine.loaders import get_basic_info, get_file_document
from app.engine.indexers.simple_index import SimpleIndex
from app.engine.chat_prompt.chat_prompt import ChatPrompt
from app.engine.chat_prompt.pydantic_prompt_models import ContractValue
from app.engine.loaders.file_parser import FileLoaderParserConfig, get_file_documents, load_config_file_parser
from app.repository.document_repository import create_database_document, get_database_document
from database.database import SessionLocal
from database import models, schemas
from llama_index.core.composability import QASummaryQueryEngineBuilder
from app.utils.regex import extract_value

document_router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@document_router.get("/")
def hello():
    return {"Hello": "World"}

@document_router.get("/query")
def query_index():
    global index


@document_router.get("/document/{document_id}")
def get_document(document_id: Annotated[str, Path(title="The ID of the document to get")]):
    return get_file_document(document_id)

@document_router.get("/document/{document_id}/basic_info")
def get_info(document_id: Annotated[str, Path(title="The ID of the document to get")], db : Session = Depends(get_db)):
    ##buscar no banco de dados se tem ja tem algum registro desse documento e dar return
    ## if (....)
    retrivied_basic_info = get_database_document(db, document_id)

    if retrivied_basic_info:
        return retrivied_basic_info


    config = load_config_file_parser()
    documents = get_file_documents(document_id, FileLoaderParserConfig(**config['file']))
    index = SimpleIndex().generate_index(documents)
    query_engine = index.as_query_engine(
        response_mode="compact"
    )

    valor_contrato_texto = query_engine.query("Me diga qual o valor total do contrato")
    base_date = query_engine.query("Me diga a data-base do valor do contrado?")
    prazo_contrato = query_engine.query("Qual o prazo do contrado?")


    # print(valor_contrato_texto.response)
    # print(extract_value(valor_contrato_texto.response)) ## REGEX SO FUNCONA PARA R$ 5000,00 OU R$XXXX,XX para outros textos nao
    print(prazo_contrato)


    # qa_query_engine_builder = QASummaryQueryEngineBuilder()
    # qa_query_engine = qa_query_engine_builder.build_from_documents(documents)

    # summary = qa_query_engine.query("Me de um summario do contrato e de seus principais pontos")

    ## todo, tentar extrair da RESPOSTA DO INDEX, joga ela num prompt para sair em um objeto estrutura
    ## 

    # print(summary)


    chat_prompt = ChatPrompt(documents=documents)
    cnpj_and_names = chat_prompt.get_cpnjs_and_names()

    db_document = schemas.DataBaseDocumentCreate(
        id=document_id, 
        contractor=cnpj_and_names.contractor, 
        contractorCNPJ=cnpj_and_names.contractor_cnpj, 
        hired=cnpj_and_names.hired, 
        hiredCNPJ=cnpj_and_names.hired_cnpj,
        contractValue=extract_value(valor_contrato_texto.response),
        baseDate=base_date.response
    )   

    create_database_document(db, db_document)



    return db_document


# endpoint to save document in contracts folder, change status return later and return object with id
@document_router.post("/upload")
async def upload_document(file: UploadFile):
    try:
        contract_id = uuid.uuid1()
        file.filename = f"{contract_id}.pdf"
        with open(f"contracts/{file.filename}", "wb+") as f:
            f.write(file.file.read())
            ## TODO salvar o pdf em base64 em algum banco de dados tambem
            
        return {"filename": file.filename, "id": contract_id }
    except Exception as e:
        return {"error": str(e)}