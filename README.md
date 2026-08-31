# TerraSync AI

**Cultivando dados. Colhendo inteligência.**

Enterprise Challenge FIAP + Oracle 2026 — Grupo 59 (Data Wars), Turma 1TSCOA.

| RM | Integrante |
|---|---|
| 568756 | Felipe Bezerra Ambrosio Sette |
| 570809 | Renan Miguel Santana Oliveira da Silva (representante) |
| 571165 | Vinicius Santos Silva |
| 572355 | Vitor Santos Mol |

## O problema

O agronegócio moderno gera dados em três formatos incompatíveis entre si: o
histórico financeiro e de safra (ERP relacional), a telemetria dos sensores de solo
no campo (IoT, JSON) e as séries climáticas (INMET, CSV). Cruzar essas fontes hoje
depende de um analista de dados e de horas de trabalho manual — tempo que uma
lavoura sob estresse hídrico não tem.

## A solução

O **TerraSync AI** centraliza as três origens em uma única base convergente (Oracle
                                                                             Database 23ai), aplica um modelo analítico de detecção precoce de risco hídrico e
entrega os resultados em um painel interativo (Power BI), permitindo que gestores e
agrônomos identifiquem talhões em risco antes que a lavoura sofra dano.

## Este repositório (evidências da Sprint 2)

```
TerraSyncAI/
├── README.md                      <- este arquivo
├── links.json                     <- link do painel publicado + vídeo pitch
├── requirements.txt
├── data/
│   ├── raw/                       <- as 3 origens sintéticas (ERP, IoT/JSON, clima/CSV)
│   ├── processed/                 <- base convergida (fato_talhao_dia) + métricas do modelo
│   └── TerraSyncAI_dataset.xlsx   <- modelo em estrela, fonte do Power BI
├── src/
│   ├── gerar_origens.py           <- gera as 3 origens de dados
│   ├── etl_convergencia.py        <- converge as origens no grão talhão-dia
│   ├── modelo_hidrico.py          <- modelo analítico de risco hídrico + validação temporal
│   └── build_powerbi_dataset.py   <- monta o modelo em estrela (star schema)
├── sql/
│   └── schema_oracle23ai.sql      <- DDL do modelo de persistência (Oracle Database 23ai)
├── powerbi/
│   └── TerraSyncAI.pbip           <- projeto Power BI completo (abrir com Power BI Desktop)
├── docs/
│   ├── arquitetura.md             <- arquitetura técnica detalhada
│   ├── roadmap.md                 <- cronograma de execução (Sprint 1, 2 e próxima evolução)
│   ├── gestao_projeto.md          <- equipe, metodologia, riscos e resposta ao feedback da Sprint 1
│   └── powerbi_guia.md            <- como abrir, revisar e publicar o painel
└── reports/figures/                <- capturas de tela do painel usadas na apresentação
```

## Como reproduzir o MVP do zero

```bash
python -m venv .venv && source .venv/bin/activate   # opcional
pip install -r requirements.txt

python src/gerar_origens.py          # materializa as 3 origens (ERP, IoT/JSON, clima/CSV)
python src/etl_convergencia.py       # converge tudo na base talhão-dia
python src/modelo_hidrico.py         # treina, valida no tempo e classifica o risco
python src/build_powerbi_dataset.py  # monta o modelo em estrela do painel
```

Depois, siga `docs/powerbi_guia.md` para abrir o painel no Power BI Desktop.

## Documentação completa

- [`docs/arquitetura.md`](docs/arquitetura.md) — arquitetura técnica, tecnologias e status de cada componente
- [`docs/roadmap.md`](docs/roadmap.md) — cronograma de execução com datas e responsáveis
- [`docs/gestao_projeto.md`](docs/gestao_projeto.md) — equipe, metodologia, riscos e como o feedback da Sprint 1 foi endereçado
- [`docs/powerbi_guia.md`](docs/powerbi_guia.md) — como abrir, revisar e publicar o painel Power BI

## Apresentação

A apresentação completa da Sprint 2 (PPTX/PDF), com o vídeo pitch, está no arquivo
enviado no portal FIAP ON e referenciada em `links.json`.
