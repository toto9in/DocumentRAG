from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Path, UploadFile, WebSocket
from fastapi.responses import FileResponse
from llama_index.core.node_parser import SentenceSplitter
from sqlalchemy.orm import Session
from app.engine.loaders import get_file_document
from app.engine.chat_prompt.chat_prompt import ChatPrompt
from app.engine.loaders.file_parser import (
    FileLoaderParserConfig,
    get_file_documents,
    load_config_file_parser,
)
from app.repository.document_repository import (
    get_database_document,
    create_db_document,
    get_db_documents,
    delete_database_document,
)
from app.repository.knowledge_base_repository import get_kb_by_id, update_kb_kb_index_id
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from database.database import SessionLocal
from database import schemas
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
def list_documents(
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    contractValue: str = None,
    status: str = None,
    baseDate: str = None,
    db: Session = Depends(get_db),
):
    return get_db_documents(db, skip, limit, name, contractValue, status, baseDate)


## todo corrigir essa rota
@document_router.get("/document/{document_id}")
def get_document(
    document_id: Annotated[str, Path(title="The ID of the document to get")],
):
    return get_file_document(document_id)


@document_router.get("/document/{document_id}/basic_info")
def get_info(
    document_id: Annotated[str, Path(title="The ID of the document to get")],
    db: Session = Depends(get_db),
):
    ##buscar no banco de dados se tem ja tem algum registro desse documento e dar return
    retrivied_basic_info = get_database_document(db, document_id)
    return retrivied_basic_info


## IMPLEMENTAR FUTURAMENTE
@document_router.get("/list/semantic_search")
def search_documents(query: str, db: Session = Depends(get_db)):
    kb = get_kb_by_id(db, 1)

    chroma_client = chromadb.HttpClient(host="chromadb")
    chroma_collection = chroma_client.get_collection(kb.name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    kb_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)
    response = kb_index.as_query_engine().query(query)
    print(response)
    for i in response.source_nodes:
        print(i)

    return response.source_nodes


## AQUI ESTA com um desempenho decente
@document_router.websocket("/{document_id}/chat")
async def websocket_endpoint(
    websocket: WebSocket, document_id: str, db: Session = Depends(get_db)
):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        chroma_client = chromadb.HttpClient(host="chromadb")
        db_document = get_database_document(db, document_id)
        chroma_collection = chroma_client.get_collection(str(db_document.index_id))
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
        index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

        chat_engine = index.as_chat_engine(
            chat_mode="openai",
            similarity_top_k=10,
        )
        streaming_response = chat_engine.stream_chat(data)
        for token in streaming_response.response_gen:
            print(token)
            await websocket.send_text(token)


@document_router.get("/{document_id}/download")
def download_document(
    document_id: Annotated[str, Path(title="The ID of the document to download")],
    db: Session = Depends(get_db),
):
    db_document = get_database_document(db, document_id)

    return FileResponse(f"contracts/{db_document.name}")


# endpoint to save document in contracts folder, change status return later and return object with id
@document_router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    try:
        kb = get_kb_by_id(db, 1)

        chroma_client = chromadb.HttpClient(host="chromadb")

        file_content = await file.read()
        with open(f"contracts/{file.filename}", "wb+") as f:
                f.write(file_content)

        config = load_config_file_parser()
        documents = get_file_documents(
            file.filename, FileLoaderParserConfig(**config["file"])
        )

        splitter = SentenceSplitter(
            chunk_size=2048,
            chunk_overlap=100,
        )

        nodes = splitter.get_nodes_from_documents(documents)

        if kb.contracts == []:
            # Se kb.contracts está vazio, crie um novo kb_index
            # chroma_collection = chroma_client.create_collection(kb.name) CRIAR COLECAO NUM OUTRO CRUD
            chroma_collection = chroma_client.get_or_create_collection(kb.name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            print("criando pela primeira vez")
            # _kb_index = VectorStoreIndex.from_documents(
            #     documents, storage_context=storage_context
            # )
            VectorStoreIndex(storage_context=storage_context, nodes=nodes)

        else:
            # Se kb.contracts não está vazio, pegue o kb_index existente e adicione o novo documento
            chroma_collection = chroma_client.get_or_create_collection(kb.name)
            vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
            print("adicionando docs")
            VectorStoreIndex.from_vector_store(vector_store=vector_store).insert_nodes(
                nodes
            )

        update_kb_kb_index_id(db, kb.id, kb.name)

        file_content_base64 = base64.b64encode(file_content).decode("utf-8")
        images = convert_from_bytes(file_content, dpi=32, first_page=1, last_page=1)
        thumbnail_io = io.BytesIO()
        images[0].save(thumbnail_io, format="PNG")
        thumbnail_base64 = base64.b64encode(thumbnail_io.getvalue()).decode("utf-8")

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

        query_engine = index.as_query_engine(
            similarity_top_k=8,
        )
        valor_contrato_texto = query_engine.query(
            "Me diga qual o valor total do contrato"
        )
        base_date = query_engine.query("Me diga a data-base do valor do contrado?")
        prazo_contrato = query_engine.query(
            "Qual o prazo/vigência do contrado? Ou seja, em quanto tempo objeto do contrato deverá ser executado?"
        )
        garantia_contrato = query_engine.query("Qual a garantia do contrato?")
        tipo_contrato = query_engine.query(
            "Dentre as categorias de contratos: seguro garantia para execução de contratos, seguro garantia para licitaçôes, seguro garantia para loteamentos, seguro garantia para retenção de pagamento, seguro garantia para processos judiciais, seguro de vida em grupo, seguro de riscos de engenharia e seguro de responsabilidade civil, qual a categoria do contrato? (pode ter mais de uma categoria)"
        )
        chat_prompt = ChatPrompt(documents=documents)
        cnpj_and_names = chat_prompt.get_cpnjs_and_names()

        db_document = schemas.DataBaseDocumentCreate(
            id=uuid.uuid1(),
            name=file.filename,
            knowledge_base_id=kb.id,
            contractor=cnpj_and_names.contractor,
            contractorCNPJ=cnpj_and_names.contractor_cnpj,
            hired=cnpj_and_names.hired,
            hiredCNPJ=cnpj_and_names.hired_cnpj,
            contractValue=extract_value(valor_contrato_texto.response),
            baseDate=base_date.response,
            contractTerm=prazo_contrato.response,
            warranty=garantia_contrato.response,
            types_of_insurances=tipo_contrato.response,
            pdf=file_content_base64,
            thumbnail=thumbnail_base64,
            index_id=simple_index_collection_id,
            status="PENDING",
        )

        ## isso aq eh para salvar no banco os doc_ids gerado no parsing para termos controle dps
        ## de quais nodes foram usados para criar e aumentar o kb_index e o index do proprio documento
        ## ajuda na hora de deletar um contrato, a deletar os nodes relacionados a ele do kb_index
        create_db_document(
            db,
            db_document,
            [node.node_id for node in nodes if node.node_id],
        )

        return {"status": "success"}
    except Exception as e:
        return {"error": str(e)}


@document_router.delete("/{document_id}")
def delete_document(
    document_id: Annotated[str, Path(title="The ID of the document to delete")],
    db: Session = Depends(get_db),
):
    chroma_client = chromadb.HttpClient(host="chromadb")

    ## primeiro pegar no banco esse db para pegar o kb_id dele e deletar esse documento do kb_index
    db_document = get_database_document(db, document_id)

    nodes_ids = []

    for doc_index in db_document.docs_index:
        nodes_ids.append(doc_index.id)

    print(nodes_ids)

    kb = get_kb_by_id(db, db_document.knowledge_base_id)
    chroma_collection = chroma_client.get_collection(kb.name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    kb_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    kb_index.delete_nodes(nodes_ids)

    delete_database_document(db, document_id)

    return {"status": "success"}
