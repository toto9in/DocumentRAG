from fastapi import FastAPI
from app.settings import init_settings
from app.controllers.document import document_router
from database.database import engine
from database import models
import uvicorn
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

load_dotenv()


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="contracts"), name="static")

init_settings()


## configurar cors e middlewares aq dps caso necessario

app.include_router(document_router, prefix="/document")

if __name__ == "__main__":
    uvicorn.run(app, port=3333)
