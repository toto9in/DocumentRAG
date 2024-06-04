from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello():
    return {"Hello": "World"}

## i'm still reading the fastapi documentation. I'll implement the api later
@app.get("/query")
def query_index():
    global index
    