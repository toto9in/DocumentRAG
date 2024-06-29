from dotenv import load_dotenv

load_dotenv()

from typing import Annotated
from fastapi import FastAPI, Path, UploadFile
from os import path, mkdir
from app.engine.loaders import get_basic_info, get_file_document
import uuid
from app.settings import init_settings
from app.controllers.document import document_router
from database.database import engine
from database import models
import uvicorn

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

init_settings()


## configurar cors e middlewares aq dps caso necessario

app.include_router(document_router, prefix="/document")

if __name__ == "__main__":
    uvicorn.run(app, port=3333)
