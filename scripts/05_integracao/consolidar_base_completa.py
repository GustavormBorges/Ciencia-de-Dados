"""Junta, por clube e temporada, todas as partidas disputadas:
liga + copas nacionais + competicoes europeias.

Entradas (data/processed/):
  partidas_por_clube.csv                  liga (Premier League e Ligue 1)
  partidas_premier_league_com_copas.csv   FA Cup e EFL Cup (feito por Vitoria)
  partidas_copas_franca_por_clube.csv     Coupe de France, Coupe de la Ligue, Trophee des Champions
  partidas_europa_por_clube.csv           Champions, Europa League, Conference League
  base_integrada.csv                      lesoes por clube e temporada (opcional)

Saidas:
  partidas_todas_competicoes.csv          uma linha por clube e temporada (396 linhas)
  base_integrada_completa.csv             o mesmo com lesoes, se base_integrada.csv existir
"""
import pandas as pd
from pathlib import Path

PASTA = Path(__file__).resolve().parents[2] / "data" / "processed"


def ler(nome):
    return pd.read_csv(PASTA / nome, encoding="utf-8-sig")


def main():
    liga = ler("partidas_por_clube.csv").rename(columns={"partidas": "partidas_liga"})
    ing = ler("partidas_premier_league_com_copas.csv")[["temporada", "clube", "partidas_facup", "partidas_eflcup"]]
    fra = ler("partidas_copas_franca_por_clube.csv").drop(columns="partidas_copas_franca")
    eur = ler("partidas_europa_por_clube.csv")[[
        "temporada", "clube", "partidas_champions", "partidas_europa_league",
        "partidas_conference_league", "partidas_europa_qualificatorias"]]

    df = liga
    for outra in (ing, fra, eur):
        df = df.merge(outra, on=["temporada", "clube"], how="left")
    colunas_novas = [c for c in df.columns if c.startswith("partidas_") and c != "partidas_liga"]
    df[colunas_novas] = df[colunas_novas].fillna(0).astype(int)

    # uma copa inglesa so existe para clubes ingleses (e vice-versa): nao deve haver cruzamento
    assert df.loc[df.liga == "Ligue 1", ["partidas_facup", "partidas_eflcup"]].sum().sum() == 0
    assert df.loc[df.liga == "Premier League", ["partidas_coupe_de_france", "partidas_coupe_de_la_ligue",
                                                 "partidas_trophee_des_champions"]].sum().sum() == 0

    df["partidas_copas_nacionais"] = (df.partidas_facup + df.partidas_eflcup + df.partidas_coupe_de_france
                                      + df.partidas_coupe_de_la_ligue + df.partidas_trophee_des_champions)
    df["partidas_europa"] = df.partidas_champions + df.partidas_europa_league + df.partidas_conference_league
    df["total_partidas"] = df.partidas_liga + df.partidas_copas_nacionais + df.partidas_europa

    ordem = ["liga", "temporada", "clube", "partidas_liga", "partidas_facup", "partidas_eflcup",
             "partidas_coupe_de_france", "partidas_coupe_de_la_ligue", "partidas_trophee_des_champions",
             "partidas_copas_nacionais", "partidas_champions", "partidas_europa_league",
             "partidas_conference_league", "partidas_europa", "partidas_europa_qualificatorias", "total_partidas"]
    df = df[ordem].sort_values(["liga", "temporada", "clube"])
    df.to_csv(PASTA / "partidas_todas_competicoes.csv", index=False, encoding="utf-8-sig")

    if (PASTA / "base_integrada.csv").exists():
        les = ler("base_integrada.csv").drop(columns=["partidas"])
        comp = df.merge(les, on=["liga", "temporada", "clube"], how="left")
        sem = comp["quantidade_lesoes"].isna().sum()
        comp.to_csv(PASTA / "base_integrada_completa.csv", index=False, encoding="utf-8-sig")
        print("base_integrada_completa.csv:", len(comp), "linhas; sem registro de lesoes:", sem)

    print("partidas_todas_competicoes.csv:", len(df), "linhas")
    print(df.groupby("liga")[["partidas_liga", "partidas_copas_nacionais", "partidas_europa", "total_partidas"]]
          .agg(["sum"]).to_string())
    print("\nMaiores cargas:")
    print(df.nlargest(5, "total_partidas")[["temporada", "clube", "partidas_liga", "partidas_copas_nacionais",
                                           "partidas_europa", "total_partidas"]].to_string(index=False))


if __name__ == "__main__":
    main()
