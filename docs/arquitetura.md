# Arquitetura Técnica — TerraSync AI

Este documento detalha a arquitetura implementada até a Sprint 2, complementando o
desenho apresentado nos slides 7 e 8 da apresentação (`EC_Sprint_2_..._DataWars.pptx`).

## 1. Visão em três camadas

```
 ORIGEM (multiformato)        MOTOR (convergência + IA)         CONSUMO
┌───────────────────┐      ┌──────────────────────────┐     ┌──────────────────┐
│ ERP (relacional)   │      │                           │     │ Dashboard Web     │
│  erp_fazendas       │      │   Oracle Database 23ai     │     │ (Power BI Service)│
│  erp_talhoes        │─────▶│   • Tabelas relacionais    │────▶│                    │
│  erp_safras         │      │   • JSON Relational        │     │ App Mobile         │
├───────────────────┤      │     Duality Views          │     │ (Power BI Mobile)  │
│ IoT (JSON)          │─────▶│   • Select AI (NL → SQL)   │     └──────────────────┘
│  sensores por talhão │      │                           │
├───────────────────┤      └──────────────────────────┘
│ INMET (CSV)         │─────▶
│  clima por região    │
└───────────────────┘
```

## 2. O que foi efetivamente implementado no MVP (Sprint 2)

| Componente | Status | Onde está no repositório |
|---|---|---|
| Geração das 3 origens (ERP, IoT/JSON, clima/CSV) | ✅ Implementado (dados sintéticos, mesma estrutura da origem real) | `src/gerar_origens.py` → `data/raw/` |
| ETL de convergência (join + tratamento + EDA) | ✅ Implementado | `src/etl_convergencia.py` → `data/processed/fato_talhao_dia.csv` |
| Modelo analítico (detecção de estresse hídrico) | ✅ Implementado e validado temporalmente | `src/modelo_hidrico.py` |
| Modelo dimensional para BI (star schema) | ✅ Implementado | `src/build_powerbi_dataset.py` → `data/TerraSyncAI_dataset.xlsx` |
| Painel Power BI (2 páginas, KPIs, filtros) | ✅ Implementado (projeto PBIP) | `powerbi/TerraSyncAI.pbip` |
| Persistência em Oracle Database 23ai | 🔶 Modelada (DDL pronto), não provisionada nesta sprint | `sql/schema_oracle23ai.sql` |
| Select AI (linguagem natural → SQL) | 🔶 Especificado (comando de exemplo no schema), depende da instância Oracle | `sql/schema_oracle23ai.sql` (seção 5) |
| App mobile / Dashboard web publicado | 🔶 Planejado para a Sprint 3, ver `docs/roadmap.md` | — |

A convenção ✅/🔶 é a mesma dos "óvalos de percentual" sugeridos no template oficial
da Sprint 2 (slide 9): usamos aqui para deixar explícito, sem ambiguidade, o que já
está de pé versus o que ainda depende da infraestrutura Oracle (que foge do escopo
de uma conta de estudante, mas está totalmente especificado em DDL pronto para uso).

## 3. Fluxo de dados ponta a ponta

1. **Ingestão**: os três formatos de origem (relacional, JSON, CSV) são gerados/capturados
   de forma independente, preservando o formato nativo de cada fonte.
2. **Convergência (ETL)**: `etl_convergencia.py` faz o *join* das três origens no grão
   *talhão-dia*, aplica limpeza (remoção de nulos, winsorização de outliers em
   `umidade_solo_pct`) e calcula uma métrica derivada (`custo_irrigacao_estimado`)
   a partir do déficit hídrico e do volume de chuva acumulado em 7 dias.
3. **Modelagem analítica**: `modelo_hidrico.py` calcula, para cada talhão/dia, a
   tendência de umidade numa janela móvel de 7 dias (regressão linear) e classifica
   o risco em `Baixo` / `Moderado` / `Alto`, com o limiar calibrado e validado
   temporalmente (ver `docs/gestao_projeto.md`, seção "Modelo analítico").
4. **Modelo dimensional**: `build_powerbi_dataset.py` materializa a tabela fato e as
   dimensões (calendário, fazenda, talhão, faixa de risco) em um único Excel, que é a
   fonte de dados do Power BI.
5. **Consumo**: o Power BI Desktop lê o Excel via Power Query (parâmetro
   `CaminhoArquivoDados`), monta o modelo em estrela com relacionamentos definidos em
   `powerbi/TerraSyncAI.SemanticModel/definition/relationships.tmdl` e expõe os
   indicadores nas duas páginas do relatório (`Visão Geral` e `Alertas e Modelo`).

## 4. Tecnologias utilizadas e o papel de cada uma

| Tecnologia | Papel na arquitetura |
|---|---|
| **Oracle Database 23ai** | Banco convergente de destino: unifica dados relacionais, JSON (via JSON Relational Duality) e permite consulta em linguagem natural via Select AI. Modelado em `sql/schema_oracle23ai.sql`. |
| **Python (pandas / numpy)** | ETL de convergência, tratamento de dados, análise exploratória e o modelo analítico de risco hídrico (regressão linear em janela móvel). |
| **openpyxl** | Materialização do modelo em estrela em um único arquivo Excel, formato intermediário entre o ETL e o Power BI. |
| **Power BI (Desktop + Service)** | Camada de consumo analítico: modelo semântico (TMDL), medidas DAX e visualizações interativas. |
| **DAX** | 13 medidas no modelo semântico (`_Medidas`), incluindo KPIs, percentuais e uma medida de cor condicional para o alerta de risco. |
| **GitHub** | Repositório técnico e versionamento de todo o código, dados de exemplo e documentação. |

## 5. Persistência de dados

O sistema de persistência é **híbrido por natureza dos dados**, conforme desenhado
desde a Sprint 1:

- **Relacional** (ERP: fazendas, talhões, safras) — chaves estrangeiras e integridade
  referencial clássica, adequado a dados financeiros e cadastrais que raramente mudam
  de estrutura.
- **Semiestruturado / JSON** (telemetria IoT) — o volume e a variabilidade dos sensores
  (nem todos os talhões têm os mesmos sensores, nem sempre sincronizam em tempo real)
  favorecem um documento JSON por leitura, consultado como view relacional via JSON
  Relational Duality do Oracle Database 23ai — o melhor dos dois mundos: flexibilidade
  de esquema na escrita, SQL padrão na leitura.
- **Dimensional** (fato_talhao_dia + dimensões) — grão talhão-dia, otimizado para
  consumo analítico no Power BI, e não para transações.
