from pydantic import BaseModel


class DataBaseDocumentCreate(BaseModel):
    id: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: str
    baseDate: str


class DataBaseDocument(BaseModel):
    id: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: str
    baseDate: str

    class Config:
        orm_mode = True

