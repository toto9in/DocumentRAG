from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from fastapi import FastAPI, Path, UploadFile
from os import path, mkdir
from app.engine.loaders import get_basic_info, get_file_document
import uuid
from app.settings import init_settings
from app.controllers.document import document_router

app = FastAPI()

init_settings()


## configurar cors e middlewares aq dps caso necessario

app.include_router(document_router, prefix="/document")

# @app.get("/")
# def hello():
#     return {"Hello": "World"}

# ## i'm still reading the fastapi documentation. I'll implement the api later
# @app.get("/query")
# def query_index():
#     global index

# ## rota para pegar um documento específico, nao implementada 100%
# ## por enquanto retornando o pdf parseado para markdown
# ## essta implementado errado, ainda falta mais etapas
# @app.get("/document/{document_id}")
# def get_document(document_id: Annotated[str, Path(title="The ID of the document to get")]):
#     return get_file_document(document_id)

# @app.get("/document/{document_id}/basic_info")
# def get_info(document_id: Annotated[str, Path(title="The ID of the document to get")]):
#     return get_basic_info(document_id)
    
# ## endpoint to save document in contracts folder, change status return later and return object with id
# @app.post("/upload")
# async def upload_document(file: UploadFile):
#     try:
#         contract_id = uuid.uuid1()
#         file.filename = f"{contract_id}.pdf"
#         with open(f"contracts/{file.filename}", "wb+") as f:
#             f.write(file.file.read())
#             ## TODO salvar o pdf em base64 em algum banco de dados tambem
            
#         return {"filename": file.filename, "id": contract_id }
#     except Exception as e:
#         return {"error": str(e)}

