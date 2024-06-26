from sqlalchemy.orm import Session
from database import models, schemas

def get_database_document(db: Session, document_id: str):
    return db.query(models.DataBaseDocument).filter(models.DataBaseDocument.id == document_id).first()

def create_database_document(db: Session, document: schemas.DataBaseDocumentCreate):
    db_document = models.DataBaseDocument(id=document.id, contractor=document.contractor, contractorCNPJ=document.contractorCNPJ, hired=document.hired, hiredCNPJ=document.hiredCNPJ, contractValue=document.contractValue, baseDate=document.baseDate)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document