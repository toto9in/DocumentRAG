from sqlalchemy.orm import Session
from database import models, schemas


def get_db_documents(db: Session, skip: int = 0, limit: int = 100):
    documents = db.query(models.DataBaseDocument).offset(skip).limit(limit).all()
    return [{key: value for key, value in document.__dict__.items() if key not in ['pdf']} for document in documents]
def get_database_document(db: Session, document_id: str):
    return db.query(models.DataBaseDocument).filter(models.DataBaseDocument.id == document_id).first()

def create_db_document_draft(db: Session, document: schemas.DataBaseDocumentDraft):
    db_document = models.DataBaseDocument(id=document.id, name=document.name, pdf=document.pdf, knowledge_base_id=document.knowledge_base_id, thumbnail=document.thumbnail)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def create_database_document(db: Session, document: schemas.DataBaseDocumentCreate):
    db_document = models.DataBaseDocument(id=document.id, contractor=document.contractor, contractorCNPJ=document.contractorCNPJ, hired=document.hired, hiredCNPJ=document.hiredCNPJ, contractValue=document.contractValue, baseDate=document.baseDate)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document