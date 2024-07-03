from sqlalchemy.orm import Session
from database import models


def get_insurrance_types_by_document_id(db: Session, document_id: str):
    return db.query(models.InsuranceNeedsAssessment).filter(
        models.InsuranceNeedsAssessment.document_id == document_id
    )
