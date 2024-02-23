-- create tables

CREATE TABLE IF NOT EXISTS public.clientes
(
    id integer NOT NULL DEFAULT nextval('clientes_id_seq'::regclass),
    limite integer,
    saldo integer,
    CONSTRAINT clientes_pkey PRIMARY KEY (id)
)

CREATE TABLE IF NOT EXISTS public.transacoes
(
    id_transacao integer NOT NULL DEFAULT nextval('transacoes_id_transacao_seq'::regclass),
    id_cliente integer NOT NULL,
    valor integer NOT NULL,
    tipo character varying COLLATE pg_catalog."default" NOT NULL,
    descricao character varying COLLATE pg_catalog."default" NOT NULL,
    realizada_em timestamp without time zone NOT NULL,
    CONSTRAINT transacoes_pkey PRIMARY KEY (id_transacao)
)

DO $$
BEGIN
  INSERT INTO clientes (nome, limite)
  VALUES
    ('o barato sai caro', 1000 * 100),
    ('zan corp ltda', 800 * 100),
    ('les cruders', 10000 * 100),
    ('padaria joia de cocaia', 100000 * 100),
    ('kid mais', 5000 * 100);
END; $$