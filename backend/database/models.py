from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
    DateTime,
    func,
    Float,
    Enum,
    Date,
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from enums.insurance_types import EInsuranceTypes
from .database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contracts = relationship("DataBaseDocument", back_populates="knowledge_base")
    kb_index_id = Column(String, nullable=True)
    createdAt = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class DataBaseDocument(Base):
    __tablename__ = "document"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    name = Column(String, index=True)
    path = Column(String)
    contractor = Column(String, nullable=True, index=True)
    contractorCNPJ = Column(String, nullable=True, index=True)
    hired = Column(String, nullable=True, index=True)
    hiredCNPJ = Column(String, nullable=True, index=True)
    contractValue = Column(Float, nullable=True, index=True)
    baseDate = Column(Date, nullable=True, index=True)
    contractTerm = Column(String, nullable=True)
    warranty = Column(String, nullable=True)
    createdAt = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=True
    )
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    index_id = Column(UUID(as_uuid=True), nullable=True)
    pdf = Column(String, nullable=True)
    thumbnail = Column(String, nullable=True)
    status = Column(String, nullable=True, index=True)
    knowledge_base_id = Column(Integer, ForeignKey("knowledge_base.id"))
    knowledge_base = relationship("KnowledgeBase", back_populates="contracts")
    docs_index = relationship("DocsIndexIds", back_populates="document")


class DocsIndexIds(Base):
    __tablename__ = "docs_index_ids"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"))
    document = relationship("DataBaseDocument", back_populates="docs_index")


class Insurance(Base):
    __tablename__ = "insurance"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(Enum(EInsuranceTypes))
    description = Column(String)


class InsuranceNeedsAssessment(Base):
    __tablename__ = "insurance_needs_assessment"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(UUID(as_uuid=True), ForeignKey("document.id"))
    insurance_id = Column(Integer)
    premium_rate = Column(Float, nullable=True)
    notes = Column(String, nullable=True)


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
