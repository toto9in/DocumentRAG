import uuid
from pydantic import BaseModel


class DataBaseDocumentUpdate(BaseModel):
    id: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: str | None
    baseDate: str
    warranty: str
    types_of_insurances: str
    contractTerm: str

class DataBaseDocumentDraft(BaseModel):
    id : uuid.UUID
    name: str
    knowledge_base_id: int
    pdf: str
    thumbnail: str
    


class DataBaseDocument(BaseModel):
    id: str
    name: str
    contractor: str
    contractorCNPJ: str
    hired: str
    hiredCNPJ: str
    contractValue: str | None
    baseDate: str
    index_id: str | None
    pdf_base: bytes | None
    knowledge_base_id: int
    class Config:
        orm_mode = True


