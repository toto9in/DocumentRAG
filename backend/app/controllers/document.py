from typing import Annotated
import uuid
from fastapi import APIRouter, Path, UploadFile

from app.engine.loaders import get_basic_info, get_file_document
from app.engine.chat_prompt.chat_prompt import ChatPrompt
from app.engine.loaders.file_parser import FileLoaderParserConfig, get_file_documents, load_config_file_parser 

document_router = APIRouter()

@document_router.get("/")
def hello():
    return {"Hello": "World"}

@document_router.get("/query")
def query_index():
    global index


@document_router.get("/document/{document_id}")
def get_document(document_id: Annotated[str, Path(title="The ID of the document to get")]):
    return get_file_document(document_id)

@document_router.get("/document/{document_id}/cnpjs_names", )
def get_info(document_id: Annotated[str, Path(title="The ID of the document to get")]):
    ##buscar no banco de dados se tem ja tem algum registro desse documento e dar return
    ## if (....)
    config = load_config_file_parser()
    documents = get_file_documents(document_id, FileLoaderParserConfig(**config['file']))
    chat_prompt = ChatPrompt(documents=documents)
    response = chat_prompt.get_cpnjs_and_names()
    ## salvar isso de cima no banco de dados
    response = chat_prompt.get_monatary_values_with_context()
    return response


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