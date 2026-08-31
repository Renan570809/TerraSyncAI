# Guia do Painel Power BI — TerraSync AI

## Como abrir

1. Baixe (ou clone) a pasta `powerbi/` inteira — ela contém `TerraSyncAI.pbip`,
   `TerraSyncAI_dataset.xlsx`, `TerraSyncAI.Report/` e `TerraSyncAI.SemanticModel/`.
   **Mantenha essas pastas juntas, no mesmo diretório** — o Power BI Desktop
   precisa enxergar `TerraSyncAI.Report` e `TerraSyncAI.SemanticModel` lado a lado
   com o arquivo `.pbip`.
2. Copie `TerraSyncAI_dataset.xlsx` para um caminho fixo no seu computador (ex.:
   `C:\Users\SEU_USUARIO\Documents\TerraSyncAI_PowerBI\TerraSyncAI_dataset.xlsx`).
3. Abra `TerraSyncAI.pbip` com o Power BI Desktop.
4. Na primeira abertura, o Power BI vai pedir para atualizar o parâmetro
   **`CaminhoArquivoDados`** (ele vem com um caminho de exemplo). Vá em
   **Editar Consultas → Gerenciar Parâmetros** e aponte para o caminho real do
   `TerraSyncAI_dataset.xlsx` no seu computador. Clique em **Atualizar**.
5. Pronto — as duas páginas (`Visão Geral` e `Alertas e Modelo`) devem carregar com
   os KPIs, filtros e gráficos.

## O que já vem montado

- **6 tabelas** em esquema estrela: 1 fato (`fato_talhao_dia`) + 4 dimensões
  (`dim_calendario`, `dim_fazenda`, `dim_talhao`, `dim_faixa_risco`) + 1 tabela de
  métricas do modelo (`dim_metricas_modelo`).
- **4 relacionamentos** entre fato e dimensões.
- **13 medidas DAX** (tabela `_Medidas`): KPIs de umidade, custo de irrigação,
  margem, precisão/recall do modelo e uma medida de cor condicional para o alerta.
- **2 páginas, 22 visuais**: cartões de KPI, 4 filtros (fazenda, cultura, faixa de
  risco, período), gráfico de linha, colunas, barras, rosca, tabela e matriz.

## Se algo não abrir corretamente

Este projeto foi escrito diretamente em formato de texto (PBIR/TMDL), sem passar
pelo Power BI Desktop — é o formato mais moderno de projeto Power BI (o mesmo que o
Desktop usa ao salvar como "Power BI Project"), mas por ter sido montado à mão,
qualquer divergência de versão do Desktop pode gerar um aviso ao abrir. Caminho
rápido caso isso aconteça (menos de 10 minutos):

1. Abra o Power BI Desktop → **Obter Dados → Excel** → selecione
   `TerraSyncAI_dataset.xlsx` → marque as 6 abas → **Carregar**.
2. Em **Gerenciar Relacionamentos**, crie as 4 relações:
   - `fato_talhao_dia[data]` → `dim_calendario[data]`
   - `fato_talhao_dia[talhao_id]` → `dim_talhao[talhao_id]`
   - `dim_talhao[fazenda_id]` → `dim_fazenda[fazenda_id]`
   - `fato_talhao_dia[faixa_risco]` → `dim_faixa_risco[faixa_risco]`
3. Cole as medidas DAX abaixo (uma nova medida por vez, em qualquer tabela):

```dax
Talhões Monitorados = DISTINCTCOUNT(fato_talhao_dia[talhao_id])
Umidade Média do Solo (%) = AVERAGE(fato_talhao_dia[umidade_solo_pct])
Dias em Alerta Alto = CALCULATE(COUNTROWS(fato_talhao_dia), fato_talhao_dia[faixa_risco] = "Alto")
% Dias em Alerta Alto = DIVIDE([Dias em Alerta Alto], COUNTROWS(fato_talhao_dia))
Custo Irrigação Total (R$) = SUM(fato_talhao_dia[custo_irrigacao_estimado])
Custo Irrigação Médio por Dia (R$) = AVERAGE(fato_talhao_dia[custo_irrigacao_estimado])
Margem Média por Hectare (R$) = AVERAGE(fato_talhao_dia[margem_estimada_ha])
Chuva Acumulada (mm) = SUM(fato_talhao_dia[chuva_mm])
Precisão do Modelo (Alerta Alto) = AVERAGE(dim_metricas_modelo[precisao_alerta])
Recall do Modelo (Alerta Alto) = AVERAGE(dim_metricas_modelo[recall_alerta])
Dias Monitorados = COUNTROWS(fato_talhao_dia)
Cor KPI Alerta = IF([% Dias em Alerta Alto] > 0.15, "#C4433B", IF([% Dias em Alerta Alto] > 0.05, "#E8A33D", "#2E6D6D"))
```

4. Monte os visuais livremente com essas medidas — sugestão de layout na tabela
   abaixo (a mesma usada no projeto original).

| Visual | Campos |
|---|---|
| 4 cartões (KPI) | Talhões Monitorados / Umidade Média / Custo Irrigação Total / Dias em Alerta Alto |
| Filtro | Fazenda, Cultura, Faixa de Risco, Período (data) |
| Linha | Eixo: `dim_calendario[data]` · Valor: Umidade Média |
| Colunas | Eixo: `dim_fazenda[fazenda_nome]` · Valor: Custo Irrigação Total |
| Barras | Eixo: `dim_talhao[cultura]` · Valor: `dim_talhao[area_ha]` |
| Rosca | Categoria: `dim_faixa_risco[faixa_risco]` · Valor: Dias Monitorados |
| Matriz | Linhas: Fazenda/Talhão · Valores: Umidade Média, % Dias em Alerta, Custo Irrigação Médio |

## Publicando

Depois de aberto e validado, publique com **Início → Publicar** (é necessária uma
conta Power BI, gratuita para alunos com e-mail institucional). Cole o link do
relatório publicado no arquivo `links.json`, na chave `"painel"` — é esse link que
vai no slide de evidências visuais e no vídeo pitch.
