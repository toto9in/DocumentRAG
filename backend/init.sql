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
    "contractor" VARCHAR,
    "contractorCNPJ" VARCHAR,
    "hired" VARCHAR,
    "hiredCNPJ" VARCHAR,
    "contractValue" VARCHAR,
    "baseDate" VARCHAR,
    "contractTerm" VARCHAR,
    "warranty" VARCHAR,
    "types_of_insurances" VARCHAR,
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

INSERT INTO public.knowledge_base
("id", "name", "kb_index_id")
VALUES(nextval('knowledge_base_id_seq'::regclass), 'TESTE', '');