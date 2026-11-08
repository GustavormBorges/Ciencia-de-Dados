import csv

with open("lesoes_distribuidas.txt", encoding="utf-8-sig") as f:
    lesoes = list(csv.DictReader(f))

with open("data/processed/partidas_por_clube.csv", encoding="utf-8-sig") as f:
    partidas = list(csv.DictReader(f))


# Correspondência dos nomes da Premier League.
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


# Correspondência dos nomes da Ligue 1.
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


clubes_partidas = set()
clubes_lesoes = set()

for linha in partidas:
    temporada = linha["temporada"]

    inicio, fim = temporada.split("/")
    temporada = inicio[-2:] + "/" + fim[-2:]

    clubes_partidas.add((
        linha["liga"],
        temporada,
        linha["clube"]
    ))


for linha in lesoes:
    liga = linha["liga_identificada"]
    temporada = linha["season_name"]
    nome = linha["clube_identificado"]

    if liga == "Premier League":
        nome_padronizado = nomes_premier.get(nome, nome)

    else:
        nome_padronizado = nomes_ligue.get(nome, nome)

    clubes_lesoes.add((
        liga,
        temporada,
        nome_padronizado
    ))


nao_encontrados = clubes_lesoes - clubes_partidas

print("=== COMPARACAO DAS BASES ===")
print("Combinações nas lesões:", len(clubes_lesoes))
print("Combinações nas partidas:", len(clubes_partidas))
print("Com correspondência:", len(clubes_lesoes) - len(nao_encontrados))
print("Sem correspondência:", len(nao_encontrados))

if nao_encontrados:
    print("\n=== CLUBES SEM CORRESPONDENCIA ===")

    for liga, temporada, clube in sorted(nao_encontrados):
        print(liga, "|", temporada, "|", clube)
