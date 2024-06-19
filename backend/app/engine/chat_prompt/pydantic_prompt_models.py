from typing import List
from pydantic import BaseModel, Field


class BasicInfo(BaseModel):
        """Data model for basic  extracted information."""

        contractor: str = Field(
            description="Nome do contrante", default='0'
        )
        contractor_cnpj: str = Field(
            description="CNPJ do contratante", default='0'
        )
        hired: str = Field(description="Nome do contratado/a", default='0')
        hired_cnpj: str = Field(description="CNPJ do contratado/a", default='0')


class MonetaryValuesAndContext(BaseModel):
        """Data model for extracting monetary values in Reais(R$) """
        valor_monetario: str = Field(
                description="Valor Monetario acompanhado do termo 'R$' com algum valor na frente, caso nao ache prencha com '0'"
        )
        contexto: str = Field(
                description="Contexto bem resumido da onde foi encontrado tal valor, caso nao encontre algo relacionado com R$, responda 'nada'"
        )

class ContractValue(BaseModel):
        """Data model for extracting contract value"""
        contract_value: str = Field(
                description="Valor total do contrato, caso nao ache prencha com '0'"
        )