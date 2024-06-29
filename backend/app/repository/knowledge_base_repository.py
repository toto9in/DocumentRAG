from sqlalchemy.orm import Session
from database import models


def get_kb_by_id(db: Session, kb_id: int):
    return (
        db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()
    )


def update_kb_kb_index_id(db: Session, kb_id: int, kb_index_id: str):
    db_kb = (
        db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()
    )
    db_kb.kb_index_id = kb_index_id
    db.commit()
    db.refresh(db_kb)
    return db_kb
