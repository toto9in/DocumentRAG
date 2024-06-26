from sqlalchemy.orm import Session
from database import models, schemas

def get_kb_by_id(db: Session, kb_id: int):
    return db.query(models.KnowledgeBase).filter(models.KnowledgeBase.id == kb_id).first()
