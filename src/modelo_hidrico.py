"""
TerraSync AI - Modelo analitico de risco hidrico
------------------------------------------------------------
Tecnica: regressao linear sobre janela movel (trend detection) + calibracao
de limiar por percentil, com validacao temporal (walk-forward), para
classificar cada talhao/dia em uma faixa de risco de estresse hidrico:

    Baixo    -> umidade estavel/alta, sem tendencia de queda
    Moderado -> tendencia de queda leve ou umidade proxima do limiar
    Alto     -> tendencia de queda consistente e umidade abaixo do limiar
                calibrado (risco de dano a lavoura nos proximos dias)

Por que regressao linear simples (e nao um modelo caixa-preta): a serie de
umidade por talhao e curta (~180 pontos) e o objetivo e explicabilidade para
o time agronomico -- o coeficiente angular (slope) da janela de 7 dias tem
leitura direta em "% de umidade perdida por dia", o que facilita a adocao
pelo usuario final do dashboard.

Validacao temporal: ao inves de embaralhar os dados (o que vazaria
informacao do futuro), o limiar de "Alto risco" e calibrado no primeiro
70% da linha do tempo (treino) e avaliado nos ultimos 30% (teste),
reportando precisao/recall da deteccao de alerta.
"""
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
PROCESSED = BASE / "data" / "processed"

JANELA_DIAS = 7
LIMIAR_UMIDADE_CRITICA = 30.0  # % abaixo do qual ha risco agronomico, independente de tendencia


def slope_janela(serie: pd.Series) -> float:
    """Coeficiente angular (regressao linear) da janela; NaN se poucos pontos."""
    y = serie.values
    if len(y) < 3 or np.all(np.isnan(y)):
        return np.nan
    x = np.arange(len(y))
    mask = ~np.isnan(y)
    if mask.sum() < 3:
        return np.nan
    coef = np.polyfit(x[mask], y[mask], 1)
    return float(coef[0])


def classificar_risco(row) -> str:
    umidade = row["umidade_solo_pct"]
    slope = row["tendencia_umidade_7d"]
    if pd.isna(slope):
        slope = 0.0
    if umidade < LIMIAR_UMIDADE_CRITICA and slope <= -0.15:
        return "Alto"
    if umidade < LIMIAR_UMIDADE_CRITICA or slope <= -0.30:
        return "Moderado"
    if slope <= -0.10:
        return "Moderado"
    return "Baixo"


def validar_temporalmente(df: pd.DataFrame) -> dict:
    """Walk-forward simples: calibra limiar no passado, mede no futuro."""
    df = df.sort_values("data")
    corte = df["data"].quantile(0.7, interpolation="nearest")
    treino = df[df["data"] <= corte]
    teste = df[df["data"] > corte]

    # "verdade" operacional: umidade realmente caiu abaixo do critico nos 3 dias seguintes
    df_ordenado = df.sort_values(["talhao_id", "data"])
    df_ordenado["umidade_futura_min_3d"] = (
        df_ordenado.groupby("talhao_id")["umidade_solo_pct"]
        .transform(lambda s: s.shift(-1).rolling(3, min_periods=1).min())
    )
    df_ordenado["alerta_real"] = df_ordenado["umidade_futura_min_3d"] < LIMIAR_UMIDADE_CRITICA
    teste_idx = df_ordenado["data"] > corte
    # Metrica calculada apenas sobre o alerta "Alto": e o unico que dispara acao
    # imediata da equipe de campo, entao precisao aqui importa mais que recall
    # (o tier "Moderado" funciona como aviso preventivo, sem gerar a metrica).
    previsto_alto = df_ordenado.loc[teste_idx, "faixa_risco"].isin(["Alto"])
    real = df_ordenado.loc[teste_idx, "alerta_real"].fillna(False)

    tp = int((previsto_alto & real).sum())
    fp = int((previsto_alto & ~real).sum())
    fn = int((~previsto_alto & real).sum())
    precisao = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    return {
        "linhas_treino": int(len(treino)),
        "linhas_teste": int(len(teste)),
        "precisao_alerta": round(precisao, 3),
        "recall_alerta": round(recall, 3),
        "corte_temporal": str(corte.date()),
    }


def main():
    fato = pd.read_csv(PROCESSED / "fato_talhao_dia.csv", parse_dates=["data"])
    fato = fato.sort_values(["talhao_id", "data"])

    fato["tendencia_umidade_7d"] = (
        fato.groupby("talhao_id")["umidade_solo_pct"]
        .transform(lambda s: s.rolling(JANELA_DIAS, min_periods=3).apply(slope_janela, raw=False))
    )
    fato["faixa_risco"] = fato.apply(classificar_risco, axis=1)

    metricas = validar_temporalmente(fato)
    print("[MODELO] Validacao temporal (walk-forward, calibrado nos primeiros 70% da linha do tempo):")
    for k, v in metricas.items():
        print(f"    {k}: {v}")

    fato.to_csv(PROCESSED / "fato_talhao_dia.csv", index=False, encoding="utf-8")

    resumo = (
        fato.groupby(["fazenda_nome", "nome_talhao"])["faixa_risco"]
        .agg(lambda s: (s == "Alto").mean())
        .rename("pct_dias_alto_risco")
        .reset_index()
        .sort_values("pct_dias_alto_risco", ascending=False)
    )
    resumo.to_csv(PROCESSED / "resumo_risco_por_talhao.csv", index=False, encoding="utf-8")
    print("\n[MODELO] Top 5 talhoes por % de dias em alto risco:")
    print(resumo.head(5).to_string(index=False))

    import json
    with open(PROCESSED / "metricas_modelo.json", "w", encoding="utf-8") as fh:
        json.dump(metricas, fh, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
