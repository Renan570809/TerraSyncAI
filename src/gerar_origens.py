"""
TerraSync AI - Geracao das origens de dados (demonstracao)
------------------------------------------------------------
Este script materializa, em formato de arquivo, as tres origens de dados
descritas na arquitetura da solucao (Sprint 1, slide 9 - "Origem Multiformato"):

  1) ERP Relacional  -> data/raw/erp_safras.csv
     Historico financeiro e de producao por talhao/safra.

  2) IoT / JSON       -> data/raw/sensores_iot.json
     Telemetria diaria de umidade do solo e pH, por talhao.

  3) INMET / CSV       -> data/raw/clima_estacoes.csv
     Series historicas de chuva e temperatura por regiao.

Os dados sao sinteticos (gerados com seed fixa para reprodutibilidade),
mas as distribuicoes e faixas de valor foram calibradas para representar
um cenario realista de fazendas de soja/milho no Centro-Oeste/Sul do Brasil.
"""
import json
import random
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

RNG_SEED = 42
random.seed(RNG_SEED)
np.random.seed(RNG_SEED)

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

FAZENDAS = [
    {"fazenda_id": 1, "nome": "Fazenda Santa Luzia", "regiao": "Sudoeste-GO", "cultura_principal": "Soja"},
    {"fazenda_id": 2, "nome": "Fazenda Boa Vista",   "regiao": "Norte-PR",    "cultura_principal": "Milho"},
    {"fazenda_id": 3, "nome": "Fazenda Rio Claro",   "regiao": "Triangulo-MG","cultura_principal": "Soja"},
    {"fazenda_id": 4, "nome": "Fazenda Cerrado Alto","regiao": "Oeste-BA",    "cultura_principal": "Algodao"},
]

TALHOES_POR_FAZENDA = 4
DATA_INICIO = date(2026, 3, 1)
DATA_FIM = date(2026, 8, 30)
N_DIAS = (DATA_FIM - DATA_INICIO).days + 1


def gerar_talhoes():
    talhoes = []
    tid = 1
    for f in FAZENDAS:
        for i in range(TALHOES_POR_FAZENDA):
            area_ha = round(random.uniform(80, 420), 1)
            talhoes.append({
                "talhao_id": tid,
                "fazenda_id": f["fazenda_id"],
                "nome_talhao": f"Lote {chr(65 + i)}",
                "area_ha": area_ha,
                "cultura": f["cultura_principal"] if random.random() > 0.15 else random.choice(
                    [c["cultura_principal"] for c in FAZENDAS]
                ),
            })
            tid += 1
    return talhoes


def gerar_erp_safras(talhoes):
    """ERP relacional: uma linha por talhao/safra com dados financeiros e de producao."""
    linhas = []
    for t in talhoes:
        custo_ha = random.uniform(3200, 5400)
        produtividade_sc_ha = {
            "Soja": random.uniform(48, 68),
            "Milho": random.uniform(95, 145),
            "Algodao": random.uniform(220, 310),
        }.get(t["cultura"], random.uniform(50, 100))
        preco_saca = {
            "Soja": random.uniform(118, 145),
            "Milho": random.uniform(55, 72),
            "Algodao": random.uniform(150, 190),
        }.get(t["cultura"], 100)
        receita_ha = produtividade_sc_ha * preco_saca
        linhas.append({
            "talhao_id": t["talhao_id"],
            "fazenda_id": t["fazenda_id"],
            "safra": "2025/2026",
            "cultura": t["cultura"],
            "area_ha": t["area_ha"],
            "custo_producao_ha": round(custo_ha, 2),
            "produtividade_sc_ha": round(produtividade_sc_ha, 1),
            "preco_saca": round(preco_saca, 2),
            "receita_estimada_ha": round(receita_ha, 2),
            "margem_estimada_ha": round(receita_ha - custo_ha, 2),
        })
    return pd.DataFrame(linhas)


def gerar_sensores_iot(talhoes):
    """IoT / JSON: leituras diarias de umidade do solo (%) e pH por talhao.

    Um subconjunto de talhoes ('lotes criticos') recebe uma tendencia de queda
    de umidade ao longo do tempo, simulando estresse hidrico -- exatamente o
    cenario que o modelo analitico (src/modelo_hidrico.py) deve aprender a
    identificar precocemente.
    """
    lotes_criticos = {t["talhao_id"] for t in talhoes if random.random() < 0.35}
    registros = []
    for t in talhoes:
        critico = t["talhao_id"] in lotes_criticos
        umidade_base = random.uniform(38, 55)
        ph_base = random.uniform(5.6, 6.8)
        for d in range(N_DIAS):
            dia = DATA_INICIO + timedelta(days=d)
            tendencia = -0.06 * d if critico else 0.0
            ruido = np.random.normal(0, 2.5)
            umidade = max(8, min(65, umidade_base + tendencia + ruido))
            ph = max(4.8, min(7.5, ph_base + np.random.normal(0, 0.12)))
            registros.append({
                "talhao_id": t["talhao_id"],
                "data": dia.isoformat(),
                "umidade_solo_pct": round(float(umidade), 2),
                "ph_solo": round(float(ph), 2),
                "temperatura_solo_c": round(float(np.random.normal(24, 3)), 1),
                "sincronizado_offline": bool(random.random() < 0.04),
            })
    return registros


def gerar_clima(talhoes):
    """INMET / CSV: chuva (mm) e temperatura (C) por regiao/dia."""
    regioes = sorted({f["regiao"] for f in FAZENDAS})
    linhas = []
    for regiao in regioes:
        chuva_media = random.uniform(3.5, 7.0)
        for d in range(N_DIAS):
            dia = DATA_INICIO + timedelta(days=d)
            sazonal = 4 * np.sin(2 * np.pi * d / 90)
            chuva = max(0, np.random.exponential(chuva_media) + sazonal - 3)
            linhas.append({
                "regiao": regiao,
                "data": dia.isoformat(),
                "chuva_mm": round(float(chuva), 1),
                "temp_media_c": round(float(np.random.normal(26, 4)), 1),
                "temp_max_c": round(float(np.random.normal(32, 4)), 1),
            })
    return pd.DataFrame(linhas)


def main():
    talhoes = gerar_talhoes()
    df_fazendas = pd.DataFrame(FAZENDAS)
    df_talhoes = pd.DataFrame(talhoes)
    df_erp = gerar_erp_safras(talhoes)
    registros_iot = gerar_sensores_iot(talhoes)
    df_clima = gerar_clima(talhoes)

    df_fazendas.to_csv(RAW_DIR / "erp_fazendas.csv", index=False, encoding="utf-8")
    df_talhoes.to_csv(RAW_DIR / "erp_talhoes.csv", index=False, encoding="utf-8")
    df_erp.to_csv(RAW_DIR / "erp_safras.csv", index=False, encoding="utf-8")
    with open(RAW_DIR / "sensores_iot.json", "w", encoding="utf-8") as fh:
        json.dump(registros_iot, fh, ensure_ascii=False, indent=2)
    df_clima.to_csv(RAW_DIR / "clima_estacoes.csv", index=False, encoding="utf-8")

    print(f"Fazendas: {len(df_fazendas)}")
    print(f"Talhoes: {len(df_talhoes)}")
    print(f"ERP (safras): {len(df_erp)} linhas -> data/raw/erp_safras.csv")
    print(f"IoT (sensores): {len(registros_iot)} leituras -> data/raw/sensores_iot.json")
    print(f"Clima (INMET): {len(df_clima)} linhas -> data/raw/clima_estacoes.csv")


if __name__ == "__main__":
    main()
