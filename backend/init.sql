CREATE TABLE knowledge_base (
    "id" SERIAL PRIMARY KEY,
    "name" VARCHAR NOT NULL,
    "kb_index_id" VARCHAR,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE document (
    "id" UUID PRIMARY KEY,
    "name" VARCHAR NOT NULL,
    "path" VARCHAR NOT NULL,
    "contractor" VARCHAR,
    "contractorCNPJ" VARCHAR,
    "hired" VARCHAR,
    "hiredCNPJ" VARCHAR,
    "contractValue" FLOAT,
    "baseDate" Date,
    "contractTerm" VARCHAR,
    "warranty" VARCHAR,
    "createdAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    "index_id" UUID,
    "pdf" TEXT,
    "thumbnail" TEXT,
    "status" VARCHAR,
    "knowledge_base_id" INTEGER REFERENCES knowledge_base("id")
);

CREATE TABLE docs_index_ids (
    "id" UUID PRIMARY KEY,
    "document_id" UUID REFERENCES document("id")
);

CREATE TYPE InsuranceType AS ENUM (
    'seguro_garantia_para_execucao_de_contratos', 
    'seguro_garantia_para_licitacoes', 
    'seguro_garantia_para_loteamentos', 
    'seguro_garantia_para_retencao_de_pagamento', 
    'seguro_garantia_para_processos_judiciais', 
    'seguro_de_vida_em_grupo', 
    'seguro_de_riscos_de_engenharia', 
    'seguro_de_responsabilidade_civil'
);

CREATE TABLE insurance (
    "id" SERIAL PRIMARY KEY,
    "name" InsuranceType,
    "description" TEXT
);

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_garantia_para_execucao_de_contratos', 'seguro garantia para execução de contratos');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_garantia_para_licitacoes', 'seguro garantia para licitaçôes');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_garantia_para_loteamentos', 'seguro garantia para loteamentos');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_garantia_para_retencao_de_pagamento', 'seguro garantia para retenção de pagamento');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_garantia_para_processos_judiciais', 'seguro garantia para processos judiciais');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_de_vida_em_grupo', 'seguro de vida em grupo');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_de_riscos_de_engenharia', 'seguro de riscos de engenharia');

INSERT INTO public.insurance
("id", "name", "description")
VALUES(nextval('insurance_id_seq'::regclass), 'seguro_de_responsabilidade_civil', 'seguro de responsabilidade civil');


CREATE TABLE insurance_needs_assessment (
    "id" SERIAL PRIMARY KEY,
    "document_id" UUID REFERENCES document(id),
    "insurance_id" INTEGER,
    "premium_rate" FLOAT,
    "notes" TEXT
);

INSERT INTO public.knowledge_base
("id", "name", "kb_index_id")
VALUES(nextval('knowledge_base_id_seq'::regclass), 'TESTE', '');