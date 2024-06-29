from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Path, UploadFile
from sqlalchemy.orm import Session
from app.engine.loaders import get_basic_info, get_file_document
from app.engine.indexers.simple_index import SimpleIndex
from app.engine.chat_prompt.chat_prompt import ChatPrompt
from app.engine.chat_prompt.pydantic_prompt_models import ContractValue
from app.engine.loaders.file_parser import FileLoaderParserConfig, get_file_documents, load_config_file_parser
from app.repository.document_repository import update_basic_info_database_document, get_database_document, create_db_document_draft, get_db_documents
from app.repository.knowledge_base_repository import get_kb_by_id, update_kb_kb_index_id
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from database.database import SessionLocal
from database import models, schemas
from llama_index.core.composability import QASummaryQueryEngineBuilder
from app.utils.regex import extract_value
import base64
import io
import chromadb
from pdf2image import convert_from_bytes

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

@document_router.get("/list")
def list_documents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_db_documents(db, skip, limit)


@document_router.get("/document/{document_id}")
def get_document(document_id: Annotated[str, Path(title="The ID of the document to get")]):
    return get_file_document(document_id)

@document_router.get("/document/{document_id}/basic_info")
def get_info(document_id: Annotated[str, Path(title="The ID of the document to get")], db : Session = Depends(get_db)):
    ##buscar no banco de dados se tem ja tem algum registro desse documento e dar return
    retrivied_basic_info = get_database_document(db, document_id)

    if retrivied_basic_info.contractor:
        return retrivied_basic_info

    config = load_config_file_parser()
    documents = get_file_documents(retrivied_basic_info.name, FileLoaderParserConfig(**config['file']))
    index = SimpleIndex().generate_index(documents) ## ESSE INDEX AQ PRECISA
    query_engine = index.as_query_engine(
        response_mode="compact"
    )

    valor_contrato_texto = query_engine.query("Me diga qual o valor total do contrato")
    base_date = query_engine.query("Me diga a data-base do valor do contrado?")
    prazo_contrato = query_engine.query("Qual o prazo/vigência do contrado? Ou seja, em quanto tempo objeto do contrato deverá ser executado?") ## SALVAR NO BANCO
    garantia_contrato = query_engine.query("Qual a garantia do contrato?") ## SALVAR NO BANCO
    tipo_contrato = query_engine.query("Dentre as categorias de contratos: seguro garantia para execução de contratos, seguro garantia para licitaçôes, seguro garantia para loteamentos, seguro garantia para retenção de pagamento, seguro garantia para processos judiciais, seguro de vida em grupo, seguro de riscos de engenharia e seguro de responsabilidade civil, qual a categoria do contrato? (pode ter mais de uma categoria)") ## SALVAR NO BANCO


    # print(valor_contrato_texto.response)
    # print(extract_value(valor_contrato_texto.response)) ## REGEX SO FUNCONA PARA R$ 5000,00 OU R$XXXX,XX para outros textos nao
    # qa_query_engine_builder = QASummaryQueryEngineBuilder()
    # qa_query_engine = qa_query_engine_builder.build_from_documents(documents)

    # summary = qa_query_engine.query("Me de um summario do contrato e de seus principais pontos")

    ## todo, tentar extrair da RESPOSTA DO INDEX, joga ela num prompt para sair em um objeto estrutura
    ## 

    # print(summary)


    chat_prompt = ChatPrompt(documents=documents)
    cnpj_and_names = chat_prompt.get_cpnjs_and_names()

    db_document = schemas.DataBaseDocumentUpdate(
        id=document_id, 
        contractor=cnpj_and_names.contractor, 
        contractorCNPJ=cnpj_and_names.contractor_cnpj, 
        hired=cnpj_and_names.hired, 
        hiredCNPJ=cnpj_and_names.hired_cnpj,
        contractValue=extract_value(valor_contrato_texto.response),
        baseDate=base_date.response,
        contractTerm=prazo_contrato.response,
        warranty=garantia_contrato.response,
        types_of_insurances=tipo_contrato.response
    )   

    update_basic_info_database_document(db, db_document)



    return db_document


@document_router.get("/list/semantic_search")
def search_documents(query: str, db: Session = Depends(get_db)):
    kb = get_kb_by_id(db, 1)

    chroma_client = chromadb.HttpClient()
    chroma_collection = chroma_client.get_collection(kb.name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    kb_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    response = kb_index.as_query_engine().query(query)
    print(response)
    for i in response.source_nodes:
        print(i)



    return response.source_nodes
    
# endpoint to save document in contracts folder, change status return later and return object with id
@document_router.post("/upload")
async def upload_document(file: UploadFile, db : Session = Depends(get_db)):
    try:
        kb = get_kb_by_id(db, 1)

        chroma_client = chromadb.HttpClient() 


        file_content = await file.read() 
        with open(f"contracts/{file.filename}", "wb+") as f:
            f.write(file_content)  

        config = load_config_file_parser()
        documents = get_file_documents(file.filename, FileLoaderParserConfig(**config['file']))
      

        print(kb.contracts)

        if kb.contracts == []:
            # Se kb.contracts está vazio, crie um novo kb_index
            # chroma_collection = chroma_client.create_collection(kb.name) CRIAR COLECAO NUM OUTRO CRUD
            chroma_collection = chroma_client.get_collection(kb.name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            print("criando pela primeira vez")
            _kb_index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
        else:
            # Se kb.contracts não está vazio, pegue o kb_index existente e adicione o novo documento
            chroma_collection = chroma_client.get_collection(kb.name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            print("adicionando docs")
            VectorStoreIndex.from_vector_store(vector_store=vector_store).insert_nodes(documents)

        update_kb_kb_index_id(db, kb.id, kb.name)

        
        file_content_base64 = base64.b64encode(file_content).decode()
        images = convert_from_bytes(file_content, dpi=32, first_page=1, last_page=1)
        thumbnail_io = io.BytesIO()
        images[0].save(thumbnail_io, format='PNG')
        thumbnail_base64 = base64.b64encode(thumbnail_io.getvalue()).decode('utf-8')

        db_document_draft = schemas.DataBaseDocumentDraft(id=uuid.uuid1(), knowledge_base_id=kb.id, name=file.filename, pdf=file_content_base64, thumbnail=thumbnail_base64)

        create_db_document_draft(db, db_document_draft)

        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}