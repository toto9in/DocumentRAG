from datetime import datetime, date
import uuid
from pydantic import BaseModel


class DataBaseDocumentUpdate(BaseModel):
    id: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: float | None
    baseDate: date
    warranty: str
    types_of_insurances: str
    contractTerm: str


class DataBaseDocumentCreate(BaseModel):
    id: uuid.UUID
    name: str
    path: str
    knowledge_base_id: int
    pdf: str
    thumbnail: str
    contractor: str | None
    contractorCNPJ: str | None
    hired: str | None
    hiredCNPJ: str | None
    contractValue: float | None
    baseDate: date
    warranty: str
    contractTerm: str | None
    index_id: uuid.UUID
    status: str


class GetDataBaseDocumentById(BaseModel):
    id: str
    name: str
    path: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: float | None
    baseDate: str
    warranty: str
    contractTerm: str
    types_of_insurances: list[int]
    pdf64: str


class DataBaseDocument(BaseModel):
    id: str
    name: str
    path: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: float | None
    baseDate: date
    index_id: str | None
    pdf_base: bytes | None
    knowledge_base_id: int

    class Config:
        orm_mode = True
