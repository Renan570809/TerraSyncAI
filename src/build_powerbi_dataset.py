"""
TerraSync AI - Monta o modelo em estrela (star schema) para o Power BI
------------------------------------------------------------
Le data/processed/fato_talhao_dia.csv (gerado por etl_convergencia.py +
modelo_hidrico.py) e produz um unico arquivo Excel com varias abas,
uma por tabela do modelo dimensional:

    fato_talhao_dia   (fato)
    dim_calendario    (dimensao)
    dim_fazenda       (dimensao)
    dim_talhao        (dimensao)
    dim_faixa_risco   (dimensao, com ordenacao para os graficos)

Esse xlsx e a fonte de dados do projeto Power BI (powerbi/TerraSyncAI/).
"""
import json
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"


def main():
    fato = pd.read_csv(PROCESSED / "fato_talhao_dia.csv", parse_dates=["data"])

    dim_calendario = pd.DataFrame({"data": pd.date_range(fato["data"].min(), fato["data"].max(), freq="D")})
    dim_calendario["ano"] = dim_calendario["data"].dt.year
    dim_calendario["mes"] = dim_calendario["data"].dt.month
    dim_calendario["nome_mes"] = dim_calendario["data"].dt.strftime("%b/%Y")
    dim_calendario["semana"] = dim_calendario["data"].dt.isocalendar().week.astype(int)
    dim_calendario["dia_semana"] = dim_calendario["data"].dt.day_name()

    dim_fazenda = fato[["fazenda_id", "fazenda_nome", "regiao"]].drop_duplicates().reset_index(drop=True)
    dim_talhao = fato[["talhao_id", "fazenda_id", "nome_talhao", "cultura", "area_ha"]].drop_duplicates().reset_index(drop=True)

    dim_faixa_risco = pd.DataFrame({
        "faixa_risco": ["Baixo", "Moderado", "Alto"],
        "ordem": [1, 2, 3],
        "cor_sugerida": ["#2E6D6D", "#E8A33D", "#C4433B"],
    })

    fato_final = fato[[
        "data", "fazenda_id", "talhao_id", "cultura",
        "umidade_solo_pct", "ph_solo", "temperatura_solo_c",
        "chuva_mm", "chuva_7d_mm", "temp_media_c", "temp_max_c",
        "custo_producao_ha", "produtividade_sc_ha", "receita_estimada_ha",
        "margem_estimada_ha", "custo_irrigacao_estimado",
        "tendencia_umidade_7d", "faixa_risco", "sincronizado_offline",
    ]].copy()

    with open(PROCESSED / "metricas_modelo.json", encoding="utf-8") as fh:
        metricas = json.load(fh)
    dim_metricas_modelo = pd.DataFrame([metricas])

    out_path = BASE / "data" / "TerraSyncAI_dataset.xlsx"
    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        fato_final.to_excel(writer, sheet_name="fato_talhao_dia", index=False)
        dim_calendario.to_excel(writer, sheet_name="dim_calendario", index=False)
        dim_fazenda.to_excel(writer, sheet_name="dim_fazenda", index=False)
        dim_talhao.to_excel(writer, sheet_name="dim_talhao", index=False)
        dim_faixa_risco.to_excel(writer, sheet_name="dim_faixa_risco", index=False)
        dim_metricas_modelo.to_excel(writer, sheet_name="dim_metricas_modelo", index=False)

    print(f"[OK] {out_path} gerado.")
    print(f"  fato_talhao_dia: {len(fato_final):,} linhas")
    print(f"  dim_calendario: {len(dim_calendario):,} linhas")
    print(f"  dim_fazenda: {len(dim_fazenda)} linhas")
    print(f"  dim_talhao: {len(dim_talhao)} linhas")


if __name__ == "__main__":
    main()
