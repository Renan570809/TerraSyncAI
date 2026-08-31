-- ============================================================================
-- TerraSync AI - Modelo de persistencia (Oracle Database 23ai)
-- ----------------------------------------------------------------------------
-- Reflete a arquitetura apresentada na Sprint 1 (slide 9): um unico banco
-- convergente (Oracle Database 23ai) capaz de tratar, na mesma engine:
--   - dados relacionais           (ERP: fazendas, talhoes, safras)
--   - dados semiestruturados JSON (telemetria dos sensores IoT, JSON Duality)
--   - series historicas simples   (clima, tratado como tabela relacional)
--
-- Este script e a referencia de "como seria em producao"; a demonstracao do
-- MVP (src/*.py) usa arquivos (CSV/JSON/XLSX) para rodar sem depender de uma
-- instancia Oracle provisionada, mas o modelo abaixo mapeia 1-para-1 com o
-- dataset gerado, para permitir migrar o MVP para o Oracle Database 23ai real
-- em uma proxima sprint.
-- ============================================================================

-- ---------------------------------------------------------------------------
-- 1) Dimensoes relacionais (origem: ERP)
-- ---------------------------------------------------------------------------
CREATE TABLE erp_fazendas (
    fazenda_id          NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nome                VARCHAR2(120)   NOT NULL,
    regiao              VARCHAR2(60)    NOT NULL,
    cultura_principal   VARCHAR2(40)
);

CREATE TABLE erp_talhoes (
    talhao_id       NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    fazenda_id      NUMBER          NOT NULL REFERENCES erp_fazendas(fazenda_id),
    nome_talhao     VARCHAR2(60)    NOT NULL,
    area_ha         NUMBER(10, 2)   NOT NULL,
    cultura         VARCHAR2(40)    NOT NULL
);

CREATE TABLE erp_safras (
    safra_id                NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    talhao_id               NUMBER          NOT NULL REFERENCES erp_talhoes(talhao_id),
    safra                   VARCHAR2(20)    NOT NULL,
    custo_producao_ha       NUMBER(12, 2),
    produtividade_sc_ha     NUMBER(10, 2),
    preco_saca              NUMBER(10, 2),
    receita_estimada_ha     NUMBER(12, 2),
    margem_estimada_ha      NUMBER(12, 2)
);

-- ---------------------------------------------------------------------------
-- 2) Origem semiestruturada (IoT) -- JSON nativo (JSON Relational Duality)
-- ---------------------------------------------------------------------------
-- O Oracle Database 23ai permite tratar o documento JSON como uma "view"
-- relacional (Duality View), sem precisar de um ETL de "achatamento" previo.
CREATE TABLE iot_leituras_raw (
    leitura_id      NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    talhao_id       NUMBER          NOT NULL REFERENCES erp_talhoes(talhao_id),
    payload         JSON            NOT NULL,   -- {"data":..,"umidade_solo_pct":..,"ph_solo":..,"temperatura_solo_c":..,"sincronizado_offline":..}
    recebido_em     TIMESTAMP       DEFAULT SYSTIMESTAMP
);

-- View relacional derivada do JSON, consumida pelo ETL/Power BI:
CREATE OR REPLACE VIEW vw_iot_leituras AS
SELECT
    leitura_id,
    talhao_id,
    JSON_VALUE(payload, '$.data'                    RETURNING DATE)           AS data,
    JSON_VALUE(payload, '$.umidade_solo_pct'         RETURNING NUMBER)         AS umidade_solo_pct,
    JSON_VALUE(payload, '$.ph_solo'                  RETURNING NUMBER)         AS ph_solo,
    JSON_VALUE(payload, '$.temperatura_solo_c'       RETURNING NUMBER)         AS temperatura_solo_c,
    JSON_VALUE(payload, '$.sincronizado_offline'     RETURNING NUMBER)         AS sincronizado_offline
FROM iot_leituras_raw;

-- ---------------------------------------------------------------------------
-- 3) Origem climatica (INMET/CSV, tratada como tabela relacional apos ingestao)
-- ---------------------------------------------------------------------------
CREATE TABLE clima_estacoes (
    regiao          VARCHAR2(60)    NOT NULL,
    data            DATE            NOT NULL,
    chuva_mm        NUMBER(8, 2),
    temp_media_c    NUMBER(6, 2),
    temp_max_c      NUMBER(6, 2),
    CONSTRAINT pk_clima PRIMARY KEY (regiao, data)
);

-- ---------------------------------------------------------------------------
-- 4) Modelo dimensional (star schema) consumido pelo Power BI
-- ---------------------------------------------------------------------------
CREATE TABLE fato_talhao_dia (
    fato_id                     NUMBER          GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    data                        DATE            NOT NULL,
    fazenda_id                  NUMBER          NOT NULL REFERENCES erp_fazendas(fazenda_id),
    talhao_id                   NUMBER          NOT NULL REFERENCES erp_talhoes(talhao_id),
    cultura                     VARCHAR2(40),
    umidade_solo_pct            NUMBER(6, 2),
    ph_solo                     NUMBER(4, 2),
    temperatura_solo_c          NUMBER(6, 2),
    chuva_mm                    NUMBER(8, 2),
    chuva_7d_mm                 NUMBER(8, 2),
    temp_media_c                NUMBER(6, 2),
    temp_max_c                  NUMBER(6, 2),
    custo_producao_ha           NUMBER(12, 2),
    produtividade_sc_ha         NUMBER(10, 2),
    receita_estimada_ha         NUMBER(12, 2),
    margem_estimada_ha          NUMBER(12, 2),
    custo_irrigacao_estimado    NUMBER(12, 2),
    tendencia_umidade_7d        NUMBER(8, 4),
    faixa_risco                 VARCHAR2(20),
    sincronizado_offline        NUMBER(1)
);

CREATE INDEX ix_fato_talhao_data ON fato_talhao_dia (talhao_id, data);
CREATE INDEX ix_fato_faixa_risco ON fato_talhao_dia (faixa_risco);

-- ---------------------------------------------------------------------------
-- 5) Select AI (linguagem natural -> SQL) -- referencia de configuracao
-- ---------------------------------------------------------------------------
-- BEGIN
--   DBMS_CLOUD_AI.CREATE_PROFILE(
--     profile_name => 'terrasync_ai_profile',
--     attributes   => '{"provider": "oracle", "object_list": [
--         {"owner": "TERRASYNC", "name": "FATO_TALHAO_DIA"},
--         {"owner": "TERRASYNC", "name": "ERP_FAZENDAS"},
--         {"owner": "TERRASYNC", "name": "ERP_TALHOES"}
--     ]}'
--   );
-- END;
-- /
-- Uso: SELECT AI 'qual talhao teve mais dias em alerta alto nos ultimos 30 dias?'
