import csv
from pathlib import Path
from datetime import datetime

base = Path(__file__).resolve().parent / "datalake" / "transfermarkt"

arquivo_lesoes = base / "player_injuries" / "player_injuries_updated_20260929.csv"
arquivo_desempenho = base / "player_performances" / "player_performances.txt"
arquivo_transferencias = base / "transfer_history" / "transfer_history.txt"

temporadas = {
    "15/16", "16/17", "17/18", "18/19", "19/20",
    "20/21", "21/22", "22/23", "23/24", "24/25"
}

ligas = {"Premier League", "Ligue 1"}

def ler(caminho):
    with open(caminho, "r", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

lesoes = ler(arquivo_lesoes)
desempenho = ler(arquivo_desempenho)
transferencias = ler(arquivo_transferencias)

clubes_temporada = {}

for linha in desempenho:
    temporada = linha["season_name"]
    liga = linha["competition_name"]

    if temporada in temporadas and liga in ligas:
        chave = (linha["player_id"], temporada)
        if chave not in clubes_temporada:
            clubes_temporada[chave] = {}

        clubes_temporada[chave].setdefault(liga, set()).add(
            linha["team_name"].strip()
        )

historico = {}

for linha in transferencias:
    try:
        data = datetime.strptime(linha["transfer_date"][:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        continue

    historico.setdefault(linha["player_id"], []).append((
        data,
        linha["from_team_name"].strip(),
        linha["to_team_name"].strip()
    ))

for jogador in historico:
    historico[jogador].sort(key=lambda x: x[0])

resultado = []

for lesao in lesoes:
    temporada = lesao["season_name"]
    jogador = lesao["player_id"]
    chave = (jogador, temporada)

    if temporada not in temporadas or chave not in clubes_temporada:
        continue

    try:
        data = datetime.strptime(lesao["from_date"][:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        continue

    clubes = clubes_temporada[chave]
    movimentos = historico.get(jogador, [])

    anteriores = [t for t in movimentos if t[0] <= data]

    clube = ""
    metodo = "Revisar"

    if anteriores:
        clube = anteriores[-1][2]
        metodo = "Historico de transferencias"
    elif movimentos:
        clube = movimentos[0][1]
        metodo = "Clube anterior a primeira transferencia"

    todos_clubes = set().union(*clubes.values())

    if clube not in todos_clubes:
        if len(todos_clubes) == 1:
            clube = next(iter(todos_clubes))
            metodo = "Unico clube na temporada"
        else:
            clube = ""
            metodo = "Revisar"

    novo = lesao.copy()
    novo["clube_identificado"] = clube
    novo["metodo_identificacao"] = metodo
    novo["status_clube"] = "Identificado" if clube else "Revisar"
    novo["competicoes_identificadas"] = "; ".join(sorted(clubes.keys()))

    resultado.append(novo)

saida = Path(__file__).resolve().parent / "lesoes_com_clube.txt"

with open(saida, "w", newline="", encoding="utf-8-sig") as f:
    campos = list(resultado[0].keys()) if resultado else []
    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultado)

identificados = sum(1 for r in resultado if r["clube_identificado"])

print("Total de registros:", len(resultado))
print("Clubes identificados:", identificados)
print("Registros para revisar:", len(resultado) - identificados)
print("Arquivo gerado:", saida)