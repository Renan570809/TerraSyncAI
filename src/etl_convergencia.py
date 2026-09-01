"""
TerraSync AI - ETL de convergencia
------------------------------------------------------------
Converge as tres origens (ERP relacional, IoT/JSON, INMET/CSV) numa base
unica no grao talhao-dia, pronta para consumo analitico (modelo_hidrico.py)
e para o modelo em estrela do Power BI (build_powerbi_dataset.py).

Etapas de tratamento de dados aplicadas (EDA + limpeza):
  - Parse e padronizacao de tipos (datas, numericos)
  - Tratamento de nulos e outliers (winsorizacao em umidade_solo_pct)
  - Join fazenda -> talhao -> IoT -> clima (por regiao/data)
  - Enriquecimento com dados financeiros do ERP (custo/receita por hectare)
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "raw"
PROCESSED = BASE / "data" / "processed"
PROCESSED.mkdir(parents=True, exist_ok=True)


def carregar_origens():
    fazendas = pd.read_csv(RAW / "erp_fazendas.csv")
    talhoes = pd.read_csv(RAW / "erp_talhoes.csv")
    erp = pd.read_csv(RAW / "erp_safras.csv")
    clima = pd.read_csv(RAW / "clima_estacoes.csv", parse_dates=["data"])
    with open(RAW / "sensores_iot.json", encoding="utf-8") as fh:
        iot = pd.DataFrame(json.load(fh))
    iot["data"] = pd.to_datetime(iot["data"])
    return fazendas, talhoes, erp, clima, iot


def tratar_outliers(df, coluna, low=0.01, high=0.99):
    """Winsorizacao simples: contem outliers nos percentis 1/99."""
    lo, hi = df[coluna].quantile([low, high])
    df[coluna] = df[coluna].clip(lo, hi)
    return df


def construir_fato_talhao_dia():
    fazendas, talhoes, erp, clima, iot = carregar_origens()

    # 1) tratamento / EDA basica
    antes = len(iot)
    iot = iot.dropna(subset=["umidade_solo_pct"])
    iot = tratar_outliers(iot, "umidade_solo_pct")
    depois = len(iot)
    print(f"[EDA] IoT: {antes - depois} linhas nulas removidas, outliers contidos (winsorizacao 1/99).")

    # 2) join talhao -> fazenda (para saber a regiao e cruzar com o clima)
    talhoes_full = talhoes.merge(fazendas[["fazenda_id", "nome", "regiao"]], on="fazenda_id", how="left")

    # 3) join IoT + talhao/fazenda
    base = iot.merge(talhoes_full, on="talhao_id", how="left")

    # 4) join clima por regiao + data
    base = base.merge(clima, on=["regiao", "data"], how="left")

    # 5) enriquecimento financeiro (ERP) -- custo/receita por hectare do talhao na safra vigente
    base = base.merge(
        erp[["talhao_id", "custo_producao_ha", "produtividade_sc_ha", "receita_estimada_ha", "margem_estimada_ha"]],
        on="talhao_id", how="left",
    )

    # 6) custo diario de irrigacao estimado (heuristica: inversamente proporcional a umidade e chuva recente)
    base = base.sort_values(["talhao_id", "data"])
    base["chuva_7d_mm"] = base.groupby("talhao_id")["chuva_mm"].transform(lambda s: s.rolling(7, min_periods=1).sum())
    deficit_hidrico = (55 - base["umidade_solo_pct"]).clip(lower=0)
    fator_chuva = 1 / (1 + base["chuva_7d_mm"] / 20)
    base["custo_irrigacao_estimado"] = (deficit_hidrico * base["area_ha"] * 3.8 * fator_chuva).round(2)

    fato = base[[
        "data", "fazenda_id", "nome", "regiao", "talhao_id", "nome_talhao", "cultura", "area_ha",
        "umidade_solo_pct", "ph_solo", "temperatura_solo_c", "chuva_mm", "chuva_7d_mm",
        "temp_media_c", "temp_max_c", "custo_producao_ha", "produtividade_sc_ha",
        "receita_estimada_ha", "margem_estimada_ha", "custo_irrigacao_estimado", "sincronizado_offline",
    ]].rename(columns={"nome": "fazenda_nome"})

    fato.to_csv(PROCESSED / "fato_talhao_dia.csv", index=False, encoding="utf-8")
    print(f"[ETL] fato_talhao_dia.csv gerado com {len(fato):,} linhas e {fato.shape[1]} colunas.")
    return fato


if __name__ == "__main__":
    construir_fato_talhao_dia()
