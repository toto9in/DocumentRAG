from pydantic import BaseModel, Field


class BasicInfo(BaseModel):
    """Data model for basic  extracted information."""

    contractor: str | None = Field(description="Nome do contrante", default=None)
    contractor_cnpj: str | None = Field(description="CNPJ do contratante", default=None)
    hired: str | None = Field(description="Nome do contratado/a", default=None)
    hired_cnpj: str | None = Field(description="CNPJ do contratado/a", default=None)


class MonetaryValuesAndContext(BaseModel):
    """Data model for extracting monetary values in Reais(R$)"""

    valor_monetario: str | None = Field(
        description="Valor Monetario acompanhado do termo 'R$' com algum valor na frente, caso nao ache prencha com none"
    )
    contexto: str | None = Field(
        description="Contexto bem resumido da onde foi encontrado tal valor, caso nao encontre algo relacionado com R$, responda 'nada'"
    )


class ContractValue(BaseModel):
    """Data model for extracting contract value"""

    contract_value: str = Field(
        description="Valor total do contrato, caso nao ache prencha com '0'"
    )
