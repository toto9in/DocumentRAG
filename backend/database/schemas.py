from pydantic import BaseModel


class DataBaseDocumentCreate(BaseModel):
    id: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str


class DataBaseDocument(BaseModel):
    id: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str

    class Config:
        orm_mode = True

