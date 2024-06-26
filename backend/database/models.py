from sqlalchemy import Boolean, Column, ForeignKey, ForeignKeyConstraint, Integer, String, Double, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base

class DataBaseDocument(Base):
    __tablename__ = "document"

    id = Column(String, primary_key=True)
    ##name = Column(String)
    ##path = Column(String)
    contractor = Column(String)
    contractorCNPJ = Column(String)
    hired = Column(String)
    hiredCNPJ = Column(String)
    contractValue = Column(String)
    baseDate = Column(String)
    ##termContract = Column(DateTime)
    createdAt = Column(DateTime(timezone=True), server_default=func.now(), nullable=True)
    updatedAt = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

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



    
    