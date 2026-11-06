import pandas as pd
from pathlib import Path

PASTAS = {"csv premier ligue": "Premier League", "csv ligue 1": "Ligue 1"}
linhas = []

for pasta, liga in PASTAS.items():
    for arq in sorted(Path(pasta).glob("*.csv")):
        ano = arq.stem                      # ex.: "15-16"
        temporada = f"20{ano[:2]}/20{ano[3:]}"
        df = pd.read_csv(arq, encoding="utf-8-sig", usecols=["HomeTeam", "AwayTeam"])
        df = df.dropna(subset=["HomeTeam", "AwayTeam"])
        # cada clube conta como mandante ou como visitante
        contagem = pd.concat([df["HomeTeam"], df["AwayTeam"]]).value_counts()
        for clube, partidas in contagem.items():
            linhas.append({"liga": liga, "temporada": temporada,
                           "clube": clube, "partidas": partidas})

res = pd.DataFrame(linhas).sort_values(["liga", "temporada", "clube"])
res.to_csv("partidas_por_clube.csv", index=False)
print(res.groupby(["liga", "temporada"])["partidas"].agg(clubes="count", min="min", max="max"))
