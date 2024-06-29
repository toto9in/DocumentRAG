from sqlalchemy.orm import Session
from database import models, schemas
from sqlalchemy import select


def get_db_documents(db: Session, skip: int = 0, limit: int = 100):
    documents = db.execute(
        select(
            models.DataBaseDocument.id,
            models.DataBaseDocument.name,
            models.DataBaseDocument.thumbnail
        ).offset(skip).limit(limit)
    ).all()
    return [{'id': doc.id, 'name': doc.name, 'thumbnail': doc.thumbnail} for doc in documents]


def get_database_document(db: Session, document_id: str):
    return db.query(models.DataBaseDocument).filter(models.DataBaseDocument.id == document_id).first()

def create_db_document_draft(db: Session, document: schemas.DataBaseDocumentDraft):
    db_document = models.DataBaseDocument(id=document.id, name=document.name, pdf=document.pdf, knowledge_base_id=document.knowledge_base_id, thumbnail=document.thumbnail)
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def update_basic_info_database_document(db: Session, document: schemas.DataBaseDocumentUpdate):
    db_document = db.query(models.DataBaseDocument).filter(models.DataBaseDocument.id == document.id).first()
    if db_document:
        db_document.contractor = document.contractor
        db_document.contractorCNPJ = document.contractorCNPJ
        db_document.hired = document.hired
        db_document.hiredCNPJ = document.hiredCNPJ
        db_document.contractValue = document.contractValue
        db_document.baseDate = document.baseDate
        db_document.warranty = document.warranty
        db_document.types_of_insurances = document.types_of_insurances
        db_document.contractTerm = document.contractTerm
        db.commit()
        db.refresh(db_document)
    return db_document