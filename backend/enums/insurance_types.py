import enum


class EInsuranceTypes(enum.Enum):
    seguro_garantia_para_execucao_de_contratos = (
        "seguro garantia para execução de contratos"
    )
    seguro_garantia_para_licitacoes = "seguro garantia para licitaçôes"
    seguro_garantia_para_loteamentos = "seguro garantia para loteamentos"
    seguro_garantia_para_retencao_de_pagamento = (
        "seguro garantia para retenção de pagamento"
    )
    seguro_garantia_para_processos_judiciais = (
        "seguro garantia para processos judiciais"
    )
    seguro_de_vida_em_grupo = "seguro de vida em grupo"
    seguro_de_riscos_de_engenharia = "seguro de riscos de engenharia"
    seguro_de_responsabilidade_civil = "seguro de responsabilidade civil"


class EInsuranceTypesId(enum.Enum):
    seguro_garantia_para_execucao_de_contratos = 1
    seguro_garantia_para_licitacoes = 2
    seguro_garantia_para_loteamentos = 3
    seguro_garantia_para_retencao_de_pagamento = 4
    seguro_garantia_para_processos_judiciais = 5
    seguro_de_vida_em_grupo = 6
    seguro_de_riscos_de_engenharia = 7
    seguro_de_responsabilidade_civil = 8


def get_insurance_type_id(insurance_types: str):
    insurance_types = insurance_types.split(",")
    insurance_types_id = []
    for insurance_type in insurance_types:
        insurance_types_id.append(int(insurance_type))
    return insurance_types_id
