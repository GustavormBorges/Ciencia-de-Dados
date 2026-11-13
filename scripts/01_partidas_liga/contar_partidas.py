import pandas as pd
from pathlib import Path
 
# Caminhos relativos a este arquivo: funciona de qualquer pasta
RAIZ = Path(__file__).resolve().parents[2]
PASTAS = {
    RAIZ / "data" / "raw" / "premier-league": "Premier League",
    RAIZ / "data" / "raw" / "ligue-1": "Ligue 1",
}
SAIDA = RAIZ / "data" / "processed" / "partidas_por_clube.csv"
 
linhas = []
 
for pasta, liga in PASTAS.items():
    arquivos = sorted(pasta.glob("*.csv"))
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {pasta}")
    for arq in arquivos:
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
SAIDA.parent.mkdir(parents=True, exist_ok=True)
res.to_csv(SAIDA, index=False)
print(res.groupby(["liga", "temporada"])["partidas"].agg(clubes="count", min="min", max="max"))