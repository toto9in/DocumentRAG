from enum import Enum
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends, Path, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
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
from app.repository.insurance_repository import get_insurrance_types_by_document_id
from app.repository.knowledge_base_repository import get_kb_by_id, update_kb_kb_index_id
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import StorageContext, VectorStoreIndex
from database.database import SessionLocal
from database import schemas
from app.utils.regex import extract_value, convert_currency_to_number
from enums.insurance_types import get_insurance_type_id
import base64
import io
import chromadb
from pdf2image import convert_from_bytes
from pydantic import BaseModel, Field
from datetime import datetime
from enums.order_by import OrderEnum
import json
import os


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
    contractValue: float = None,
    orderValuesBy: OrderEnum = None,
    status: str = None,
    baseDate: str = None,
    orderDatesBy: OrderEnum = None,
    db: Session = Depends(get_db),
):
    return get_db_documents(
        db,
        skip,
        limit,
        name,
        contractValue,
        status,
        baseDate,
        orderValuesBy,
        orderDatesBy,
    )


@document_router.get("/document/{document_id}")
def get_document_by_id(
    document_id: Annotated[str, Path(title="The ID of the document to get")],
    db: Session = Depends(get_db),
):
    ##buscar no banco de dados se tem ja tem algum registro desse documento e dar return
    retrivied_basic_info = get_database_document(db, document_id)
    retrievied_insurance_types = get_insurrance_types_by_document_id(db, document_id)
    if not retrivied_basic_info:
        return JSONResponse(
            status_code=404, content={"error": "Documento não encontrado"}
        )
    if not retrievied_insurance_types:
        return JSONResponse(
            status_code=404,
            content={
                "error": "Tipos de seguro não encontrados, pode ter ocorrido um erro no processamento do documento"
            },
        )

    insurance_types = []
    for retrieved_insurance_type in retrievied_insurance_types:
        insurance_types.append(retrieved_insurance_type.insurance_id)

    responseModel = schemas.GetDataBaseDocumentById(
        id=str(retrivied_basic_info.id),
        name=retrivied_basic_info.name,
        path=retrivied_basic_info.path,
        contractor=retrivied_basic_info.contractor,
        contractorCNPJ=retrivied_basic_info.contractorCNPJ,
        hired=retrivied_basic_info.hired,
        hiredCNPJ=retrivied_basic_info.hiredCNPJ,
        contractValue=retrivied_basic_info.contractValue,
        baseDate=str(retrivied_basic_info.baseDate),
        warranty=retrivied_basic_info.warranty,
        contractTerm=retrivied_basic_info.contractTerm,
        types_of_insurances=insurance_types,
        pdf64=retrivied_basic_info.pdf,
    )

    return JSONResponse(status_code=200, content={"data": responseModel.model_dump()})


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
    try:
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
            streaming_response = chat_engine.chat(data)
            print(streaming_response.response)
            await websocket.send_text(streaming_response.response)
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for document_id: {document_id}")
    except Exception as e:
        print(f"An error occurred: {e}")


@document_router.get("/{document_id}/download")
def download_document(
    document_id: Annotated[str, Path(title="The ID of the document to download")],
    db: Session = Depends(get_db),
):
    db_document = get_database_document(db, document_id)
    if not db_document:
        return JSONResponse(
            status_code=404, content={"error": "Documento não encontrado"}
        )

    modified_path = db_document.path.replace("/static/", "")

    return FileResponse(f"contracts/{modified_path}")


# endpoint to save document in contracts folder, change status return later and return object with id
@document_router.post("/upload")
async def upload_document(file: UploadFile, db: Session = Depends(get_db)):
    try:
        kb = get_kb_by_id(db, 1)

        ## no docker tem que passar pro HttpClient(host="chromadb")
        ## para uso local tire
        chroma_client = chromadb.HttpClient(host="chromadb")

        file_content = await file.read()
        original_name = file.filename
        name = os.path.splitext(original_name)[0]
        name_without_spaces = original_name.replace(" ", "").lower()

        name_part, extension = os.path.splitext(name_without_spaces)
        unique_id = uuid.uuid1()

        new_file_name = f"{name_part}{unique_id}{extension}"

        new_file_path = os.path.join("contracts", new_file_name)

        with open(new_file_path, "wb+") as f:
            f.write(file_content)

        config = load_config_file_parser()
        documents = get_file_documents(
            new_file_name, FileLoaderParserConfig(**config["file"])
        )

        splitter = SentenceSplitter(
            chunk_size=2048,
            chunk_overlap=100,
        )

        nodes = splitter.get_nodes_from_documents(documents)

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

        chat_prompt = ChatPrompt(documents=documents)
        cnpj_and_names = chat_prompt.get_cpnjs_and_names()

        query_engine = index.as_query_engine(
            response_mode="compact",
            similarity_top_k=10,
        )

        valor_contrato_texto = query_engine.query(
            "Me diga qual o valor total do contrato"
        )

        extracted_value_str = extract_value(
            valor_contrato_texto.response
        )  ## mudar na modelagem do banco para float, editar pdf com valores reais

        if (
            cnpj_and_names is None
            or cnpj_and_names.contractor is None
            or cnpj_and_names.contractor_cnpj is None
            and cnpj_and_names.hired is None
            and cnpj_and_names.hired_cnpj is None
            and extracted_value_str is None
        ):
            os.remove(f"contracts/{file.filename}")

            return JSONResponse(
                status_code=406, content={"error": "Documento invalido"}
            )

        print(extracted_value_str)
        number_contract_value = convert_currency_to_number(extracted_value_str)
        print(number_contract_value)
        base_date = query_engine.query(
            "Me diga a data-base do valor do contrato se houver, ou o dia que tem que pagar o contrato? Retorne em json sendo o campo data_base no formato dd/mm/aaaa caso ache, caso contrário coloque null nesse campo"
        )
        base_date_value = json.loads(base_date.response)["data_base"]

        data_object = datetime.strptime(base_date_value, "%d/%m/%Y").date()

        prazo_contrato = query_engine.query(
            "Qual o prazo/vigência do contrato? Ou seja, em quanto tempo o objeto do contrato deverá ser executado? Retorne em json sendo o campo vigencia_contrato caso ache, caso contrário coloque null nesses campos"
        )
        prazo_contrato_value = json.loads(prazo_contrato.response)["vigencia_contrato"]

        garantia_contrato = query_engine.query(
            "Qual a garantia do contrato se houver? Responda resumidamente em até 2 linhas"
        )

        tipo_seguros = query_engine.query(
            """
            Dentre as seguintes categorias de seguros, identifique a categoria ou as categorias que se aplicam ao contrato fornecido:

            1. Seguro Garantia para Execução de Contratos: Garanta as assinaturas de contratos públicos ou privados. \n
            2. Seguro Garantia para Licitações: Apresente garantias para sua licitação rapidamente. \n
            3. Seguro Garantia para Loteamentos: Realize obras de loteamentos e garanta as exigências necessárias. \n
            4. Seguro Garantia para Retenção de Pagamento: Recupere o pagamento de valores retidos ao fim de contratos. \n
            5. Seguro Garantia para Processos Judiciais: Substitua e libere bens e valores depositados em juízo. \n
            6. Seguro de Vida em Grupo: Cuide das pessoas que trabalham na sua empresa. \n
            7. Seguro de Riscos de Engenharia: Proteja-se contra os riscos que podem afetar a sua obra. \n
            8. Seguro de Responsabilidade Civil: Garanta segurança contra qualquer tipo de imprevisto. \n

            Qual(is) categoria(s) de seguro se aplicam a este contrato específico? Retorne em json sendo o campo tipo_seguro a lista de numeros caso ache, caso contrário coloque null nesses campos
            """
        )

        tipos_seguros_value = json.loads(tipo_seguros.response)["tipo_seguro"]
        file_content_base64 = base64.b64encode(file_content).decode("utf-8")
        images = convert_from_bytes(file_content, dpi=32, first_page=1, last_page=1)
        thumbnail_io = io.BytesIO()
        images[0].save(thumbnail_io, format="PNG")
        thumbnail_base64 = base64.b64encode(thumbnail_io.getvalue()).decode("utf-8")

        db_document = schemas.DataBaseDocumentCreate(
            id=uuid.uuid1(),
            name=name,
            path=f"/static/{new_file_name}",
            knowledge_base_id=kb.id,
            contractor=cnpj_and_names.contractor,
            contractorCNPJ=cnpj_and_names.contractor_cnpj,
            hired=cnpj_and_names.hired,
            hiredCNPJ=cnpj_and_names.hired_cnpj,
            contractValue=number_contract_value,
            baseDate=data_object,
            contractTerm=str(prazo_contrato_value),
            warranty=str(garantia_contrato.response),
            pdf=file_content_base64,
            thumbnail=thumbnail_base64,
            index_id=simple_index_collection_id,
            status="PENDING",
        )

        insurance_types_ids = list(tipos_seguros_value)

        ## isso aq eh para salvar no banco os doc_ids gerado no parsing para termos controle dps
        ## de quais nodes foram usados para criar e aumentar o kb_index e o index do proprio documento
        ## ajuda na hora de deletar um contrato, a deletar os nodes relacionados a ele do kb_index
        create_db_document(
            db,
            db_document,
            [node.node_id for node in nodes if node.node_id],
            insurance_types_ids,
        )

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

        return JSONResponse(
            status_code=200, content={"success": "Documento salvo com sucesso"}
        )
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
    if not db_document:
        return JSONResponse(
            status_code=404, content={"error": "Documento não encontrado"}
        )

    nodes_ids = []

    for doc_index in db_document.docs_index:
        nodes_ids.append(str(doc_index.id))

    kb = get_kb_by_id(db, db_document.knowledge_base_id)
    chroma_collection = chroma_client.get_collection(kb.name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    kb_index = VectorStoreIndex.from_vector_store(vector_store=vector_store)

    kb_index.delete_nodes(nodes_ids)

    delete_database_document(db, document_id)

    return JSONResponse(
        status_code=200, content={"success": "Documento deletado com sucesso"}
    )
