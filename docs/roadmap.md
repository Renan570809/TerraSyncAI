# Roadmap de Execução — TerraSync AI

O feedback da Sprint 1 apontou falta de clareza no roadmap. Este documento substitui
o quadro Kanban genérico usado anteriormente por um cronograma real, com datas,
entregas e responsáveis por frente de trabalho.

## Linha do tempo geral do Challenge

| Fase | Período | Status |
|---|---|---|
| Sprint 1 — Ideação e arquitetura inicial | 25/05 a 16/06/2026 | ✅ Concluída (nota 6,5/10 — feedback incorporado nesta sprint) |
| Sprint 2 — MVP e evidências de construção | 03/08 a 01/09/2026 | ✅ Concluída (esta entrega) |
| Avaliação individual + seleção dos 6 finalistas | 02/09 a 13/09/2026 | 🔜 Aguardando |
| Apresentação ao vivo para a banca (Top 6) | 14/09 a 18/09/2026, 19h30 (Teams) | 🔜 Planejada |
| Evento NEXT 2026 (final, Top 3) | A definir pela FIAP/Oracle | 🔜 Planejada |

## Frentes de trabalho da Sprint 2 (03/08 – 01/09/2026)

| Semana | Frente | Entrega | Responsável |
|---|---|---|---|
| 03–09/08 | Dados | Geração das 3 origens sintéticas (ERP, IoT/JSON, clima/CSV) com volume e distribuição realistas | Vitor Santos Mol |
| 03–09/08 | Gestão | Atualização da documentação de gestão (Sprint 1) e divisão das frentes técnicas | Renan Miguel S. O. da Silva |
| 10–16/08 | Engenharia de dados | ETL de convergência: join das origens no grão talhão-dia, tratamento de nulos/outliers | Vinicius Santos Silva |
| 10–16/08 | Modelagem | Definição do modelo dimensional (star schema) para consumo analítico | Felipe Bezerra A. Sette |
| 17–23/08 | Ciência de dados | Modelo analítico de risco hídrico (regressão em janela móvel) + validação temporal | Vinicius Santos Silva |
| 17–23/08 | Persistência | Modelagem do schema Oracle Database 23ai (DDL + JSON Duality + Select AI) | Felipe Bezerra A. Sette |
| 24–29/08 | BI | Construção do painel Power BI (modelo semântico, medidas DAX, 2 páginas de visuais) | Renan Miguel S. O. da Silva |
| 24–29/08 | Repositório | Criação do repositório técnico público no GitHub, README e documentação | Renan Miguel S. O. da Silva |
| 30–31/08 | Entrega | Consolidação da apresentação, revisão geral, gravação do vídeo pitch | Todo o grupo |

## Próxima evolução (pós-Sprint 2, caso o grupo avance ao Top 6)

| Item | Descrição |
|---|---|
| Provisionar Oracle Database 23ai real | Migrar o schema de `sql/schema_oracle23ai.sql` para uma instância OCI, substituindo os arquivos por conexões vivas. |
| Ativar Select AI | Conectar o perfil de IA generativa às tabelas reais, permitindo perguntas em linguagem natural no dashboard. |
| Publicar o painel no Power BI Service | Disponibilizar o link público/organizacional do relatório (hoje o projeto roda localmente via PBIP). |
| Ingestão em tempo real dos sensores IoT | Substituir a geração sintética por um endpoint de ingestão (ex.: Oracle REST Data Services) que recebe o JSON dos sensores de fato. |
| App mobile | Protótipo de consumo mobile dos KPIs críticos (hoje representado apenas no protótipo de tela, Sprint 1). |

## Gestão ágil

O grupo trabalhou em ciclos semanais dentro da Sprint 2, com reuniões curtas de
alinhamento entre as frentes (dados, modelagem, BI e repositório) para garantir que
a saída de uma etapa (ex.: `fato_talhao_dia.csv`) estivesse pronta a tempo de
alimentar a etapa seguinte (o modelo analítico e, depois, o Power BI). O quadro de
tarefas do grupo (backlog/to do/doing/concluído) foi mantido para o dia a dia, mas o
roadmap acima é a referência oficial de prazos e responsáveis para efeito de
avaliação.
