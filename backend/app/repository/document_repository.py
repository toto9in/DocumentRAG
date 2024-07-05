from typing import List
from sqlalchemy.orm import Session
from database import models, schemas
from sqlalchemy import and_, cast, String, func, select
from enums.order_by import OrderEnum


def get_db_documents(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: str = None,
    contractValue: float = None,
    status: str = None,
    baseDate: str = None,
    orderValuesBy: OrderEnum = None,
    orderDatesBy: OrderEnum = None,
):
    query = select(
        models.DataBaseDocument.id,
        models.DataBaseDocument.name,
        models.DataBaseDocument.path,
        models.DataBaseDocument.contractValue,
        models.DataBaseDocument.status,
        models.DataBaseDocument.baseDate,
    )

    filters = []
    if name is not None:
        filters.append(models.DataBaseDocument.name.ilike(f"%{name}%"))
    if contractValue is not None:
        filters.append(models.DataBaseDocument.contractValue == contractValue)
    if status is not None:
        filters.append(models.DataBaseDocument.status.ilike(f"%{status}%"))
    if baseDate is not None:
        filters.append(
            cast(models.DataBaseDocument.baseDate, String).ilike(f"%{baseDate}%")
        )

    if filters:
        query = query.where(and_(*filters))

    if orderValuesBy is not None:
        if orderValuesBy == OrderEnum.ASC:
            query = query.order_by(models.DataBaseDocument.contractValue.asc())
        elif orderValuesBy == OrderEnum.DESC:
            query = query.order_by(models.DataBaseDocument.contractValue.desc())

    if orderDatesBy is not None:
        if orderDatesBy == OrderEnum.ASC:
            query = query.order_by(models.DataBaseDocument.baseDate.asc())
        elif orderDatesBy == OrderEnum.DESC:
            query = query.order_by(models.DataBaseDocument.baseDate.desc())

    total_query = select(func.count()).select_from(query.subquery())
    total = db.execute(total_query).scalar()

    documents = db.execute(query.offset(skip).limit(limit)).fetchall()

    return {
        "total": total,
        "documents": [
            {
                "id": doc.id,
                "name": doc.name,
                "path": doc.path,
                "status": doc.status,
                "baseDate": doc.baseDate,
                "contractValue": doc.contractValue,
            }
            for doc in documents
        ],
    }


def get_database_document(db: Session, document_id: str):
    return (
        db.query(models.DataBaseDocument)
        .filter(models.DataBaseDocument.id == document_id)
        .first()
    )


def delete_database_document(db: Session, document_id: str):
    db_document = (
        db.query(models.DataBaseDocument)
        .filter(models.DataBaseDocument.id == document_id)
        .first()
    )
    if db_document:
        db.execute(
            models.InsuranceNeedsAssessment.__table__.delete().where(
                models.InsuranceNeedsAssessment.document_id == document_id
            )
        )

        db.delete(db_document)
        db.commit()
    return db_document


def create_db_document(
    db: Session,
    document: schemas.DataBaseDocumentCreate,
    index_ids: List[String],
    insurance_types_ids: List[int],
):
    db_document = models.DataBaseDocument(
        id=document.id,
        name=document.name,
        path=document.path,
        pdf=document.pdf,
        knowledge_base_id=document.knowledge_base_id,
        thumbnail=document.thumbnail,
        contractor=document.contractor,
        contractorCNPJ=document.contractorCNPJ,
        hired=document.hired,
        hiredCNPJ=document.hiredCNPJ,
        contractValue=document.contractValue,
        baseDate=document.baseDate,
        warranty=document.warranty,
        contractTerm=document.contractTerm,
        index_id=document.index_id,
        status=document.status,
    )

    db_index_ids = [
        models.DocsIndexIds(id=index_id, document_id=document.id)
        for index_id in index_ids
    ]

    db_insurances = [
        models.InsuranceNeedsAssessment(
            document_id=document.id, insurance_id=insurance_id
        )
        for insurance_id in insurance_types_ids
    ]

    db.add(db_document)
    db.add_all(db_index_ids)
    db.add_all(db_insurances)
    db.commit()
    db.refresh(db_document)
    return db_document


def update_basic_info_database_document(
    db: Session, document: schemas.DataBaseDocumentUpdate
):
    db_document = (
        db.query(models.DataBaseDocument)
        .filter(models.DataBaseDocument.id == document.id)
        .first()
    )
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
