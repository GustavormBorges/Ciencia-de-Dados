
import csv
from pathlib import Path

base = Path(__file__).resolve().parent


def ler(arquivo):
    with open(base / arquivo, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def padronizar_temporada(temporada):
    inicio, fim = temporada.split("/")
    return inicio[-2:] + "/" + fim[-2:]


nomes_premier = {
    "AFC Bournemouth": "Bournemouth",
    "Arsenal FC": "Arsenal",
    "Aston Villa": "Aston Villa",
    "Brentford FC": "Brentford",
    "Brighton & Hove Albion": "Brighton",
    "Burnley FC": "Burnley",
    "Cardiff City": "Cardiff",
    "Chelsea FC": "Chelsea",
    "Crystal Palace": "Crystal Palace",
    "Everton FC": "Everton",
    "Fulham FC": "Fulham",
    "Huddersfield Town": "Huddersfield",
    "Hull City": "Hull",
    "Ipswich Town": "Ipswich",
    "Leeds United": "Leeds",
    "Leicester City": "Leicester",
    "Liverpool FC": "Liverpool",
    "Luton Town": "Luton",
    "Manchester City": "Man City",
    "Manchester United": "Man United",
    "Middlesbrough FC": "Middlesbrough",
    "Newcastle United": "Newcastle",
    "Norwich City": "Norwich",
    "Nottingham Forest": "Nott'm Forest",
    "Sheffield United": "Sheffield United",
    "Southampton FC": "Southampton",
    "Stoke City": "Stoke",
    "Sunderland AFC": "Sunderland",
    "Swansea City": "Swansea",
    "Tottenham Hotspur": "Tottenham",
    "Watford FC": "Watford",
    "West Bromwich Albion": "West Brom",
    "West Ham United": "West Ham",
    "Wolverhampton Wanderers": "Wolves"
}


nomes_ligue = {
    "AC Ajaccio": "Ajaccio",
    "AJ Auxerre": "Auxerre",
    "AS Monaco": "Monaco",
    "AS Nancy-Lorraine": "Nancy",
    "AS Saint-Étienne": "St Etienne",
    "Amiens SC": "Amiens",
    "Angers SCO": "Angers",
    "Clermont Foot 63": "Clermont",
    "Dijon FCO": "Dijon",
    "EA Guingamp": "Guingamp",
    "ESTAC Troyes": "Troyes",
    "FC Girondins Bordeaux": "Bordeaux",
    "FC Lorient": "Lorient",
    "FC Metz": "Metz",
    "FC Nantes": "Nantes",
    "FC Toulouse": "Toulouse",
    "GFC Ajaccio": "Ajaccio GFCO",
    "LOSC Lille": "Lille",
    "Le Havre AC": "Le Havre",
    "Montpellier HSC": "Montpellier",
    "Nîmes Olympique": "Nimes",
    "OGC Nice": "Nice",
    "Olympique Lyon": "Lyon",
    "Olympique Marseille": "Marseille",
    "Paris Saint-Germain": "Paris SG",
    "RC Lens": "Lens",
    "RC Strasbourg Alsace": "Strasbourg",
    "SC Bastia": "Bastia",
    "SM Caen": "Caen",
    "Stade Brestois 29": "Brest",
    "Stade Reims": "Reims",
    "Stade Rennais FC": "Rennes"
}


lesoes = ler("lesoes_distribuidas.txt")
partidas = ler("data/processed/partidas_por_clube.csv")


# Agrupa as lesões por liga, temporada e clube.
agrupamento_lesoes = {}

for linha in lesoes:
    liga = linha["liga_identificada"]
    temporada = linha["season_name"]
    nome = linha["clube_identificado"]

    if liga == "Premier League":
        nome_padronizado = nomes_premier[nome]
    else:
        nome_padronizado = nomes_ligue[nome]

    chave = (liga, temporada, nome_padronizado)

    if chave not in agrupamento_lesoes:
        agrupamento_lesoes[chave] = {
            "dias": 0,
            "lesoes": set()
        }

    agrupamento_lesoes[chave]["dias"] += int(
        linha["days_missed_clube"]
    )

    agrupamento_lesoes[chave]["lesoes"].add(
        linha["id_lesao"]
    )


# Integra as lesões com os dados de partidas.
resultado = []
combinacoes_partidas = set()

for linha in partidas:
    liga = linha["liga"]
    temporada_completa = linha["temporada"]
    temporada = padronizar_temporada(temporada_completa)
    clube = linha["clube"]

    chave = (liga, temporada, clube)
    combinacoes_partidas.add(chave)

    informacoes = agrupamento_lesoes.get(chave)

    if informacoes:
        quantidade_lesoes = len(informacoes["lesoes"])
        dias_ausencia = informacoes["dias"]
    else:
        quantidade_lesoes = 0
        dias_ausencia = 0

    resultado.append({
        "liga": liga,
        "temporada": temporada_completa,
        "clube": clube,
        "partidas": linha["partidas"],
        "quantidade_lesoes": quantidade_lesoes,
        "dias_ausencia": dias_ausencia
    })


# Confere se todas as combinações de lesões foram integradas.
combinacoes_lesoes = set(agrupamento_lesoes.keys())
sem_correspondencia = combinacoes_lesoes - combinacoes_partidas


# Salva a base integrada.
arquivo_saida = base / "data" / "processed" / "base_integrada.csv"

with open(arquivo_saida, "w", newline="", encoding="utf-8-sig") as f:
    campos = [
        "liga",
        "temporada",
        "clube",
        "partidas",
        "quantidade_lesoes",
        "dias_ausencia"
    ]

    escritor = csv.DictWriter(f, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(resultado)


print("=== INTEGRACAO DAS BASES ===")
print("Combinações de partidas:", len(combinacoes_partidas))
print("Combinações de lesões:", len(combinacoes_lesoes))
print("Linhas na base integrada:", len(resultado))
print("Combinações sem correspondência:", len(sem_correspondencia))
print("Arquivo gerado:", arquivo_saida)
