INSERT INTO public.knowledge_base
(id, "name", kb_index_id, "createdAt", "updatedAt")
VALUES(nextval('knowledge_base_id_seq'::regclass), 'TESTE', '', now(), now());