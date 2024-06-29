from sqlalchemy import Boolean, Column, ForeignKey, ForeignKeyConstraint, Integer, String, Double, DateTime, func, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import base64
from .database import Base

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contracts = relationship("DataBaseDocument", back_populates="knowledge_base")
    kb_index_id = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

class DataBaseDocument(Base):
    __tablename__ = "document"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, index=True)
    ##path = Column(String)
    contractor = Column(String, nullable=True, index=True)
    contractorCNPJ = Column(String, nullable=True, index=True)
    hired = Column(String, nullable=True, index=True)
    hiredCNPJ = Column(String, nullable=True, index=True)
    contractValue = Column(String, nullable=True)
    baseDate = Column(String, nullable=True)
    contractTerm = Column(String, nullable=True)
    warranty = Column(String, nullable=True)
    types_of_insurances = Column(String, nullable=True)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    index_id = Column(String, nullable=True)
    pdf = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)

    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    knowledge_base = relationship("KnowledgeBase", back_populates="contracts")



# class Company(Base):
#     __tablename__ = "company"

#     id = Column(String, primary_key=True)
#     name = Column(String)
#     cnpj = Column(String, primary_key=True, unique=True)
#     createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
#     updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
#     companyDocument = relationship("CompanyDocument", backref="company")

# class CompanyDocuments(Base):
#     __tablename__ = "company_documents"

#     id = Column(String, primary_key=True)
#     cnpj = Column(String, ForeignKey("company.cnpj"), unique=True)
#     document_id = Column(String, ForeignKey("document.id"))
#     createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
#     updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

#     __table_args__ = (
#         ForeignKeyConstraint([cnpj], ['company.cnpj'], ondelete='CASCADE', name='fk_company_documents_company_cnpj'),
#     )



    
    