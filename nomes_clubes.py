"""Padronizacao de nomes de clubes das novas fontes (RSSSF e Wikipedia)
para os nomes usados em data/processed/partidas_por_clube.csv (estilo Football-Data).

So entram aqui clubes da Premier League e da Ligue 1. Qualquer outro time
(adversarios estrangeiros, clubes amadores) fica com o nome original e NAO e
contado. Um nome so vira clube da liga se o clube estava na liga naquela
temporada (verificado em clube_na_liga).
"""
import csv
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
ARQ_PARTIDAS = RAIZ / "data" / "processed" / "partidas_por_clube.csv"


def normalizar(nome):
    nome = unicodedata.normalize("NFKD", nome).encode("ascii", "ignore").decode()
    return " ".join(nome.lower().replace("-", " ").replace(".", " ").split())


def _dic(pares):
    return {normalizar(k): v for k, v in pares.items()}


# Premier League (nomes que aparecem nas competicoes europeias)
PL = _dic({
    "Arsenal": "Arsenal",
    "Aston Villa (Birmingham)": "Aston Villa", "Aston Villa": "Aston Villa",
    "Brighton & Hove Albion": "Brighton", "Brighton and Hove Albion": "Brighton",
    "Burnley": "Burnley",
    "Chelsea": "Chelsea",
    "Everton": "Everton",
    "Leicester City": "Leicester", "Leicester": "Leicester",
    "Liverpool": "Liverpool",
    "Manchester City": "Man City", "Manchester United": "Man United",
    "Newcastle United": "Newcastle",
    "Southampton": "Southampton",
    "Tottenham Hotspur": "Tottenham", "Tottenham": "Tottenham",
    "West Ham United": "West Ham", "West Ham": "West Ham",
    "Wolverhampton Wanderers": "Wolves", "Wolves": "Wolves",
})

# Ligue 1 (Europa + copas francesas; RSSSF e Wikipedia)
L1 = _dic({
    "Ajaccio": "Ajaccio", "AC Ajaccio": "Ajaccio", "Ajaccio AC": "Ajaccio",
    "Gazelec Ajaccio": "Ajaccio GFCO", "GFC Ajaccio": "Ajaccio GFCO",
    "Amiens": "Amiens", "Amiens SC": "Amiens",
    "Angers": "Angers", "Angers SCO": "Angers",
    "Auxerre": "Auxerre",
    "Bastia": "Bastia", "SC Bastia": "Bastia",
    "Bordeaux": "Bordeaux", "Girondins (Bordeaux)": "Bordeaux", "Girondins Bordeaux": "Bordeaux",
    "Brest": "Brest", "Stade Brestois": "Brest",
    "Caen": "Caen",
    "Clermont": "Clermont", "Clermont Foot": "Clermont",
    "Dijon": "Dijon",
    "Guingamp": "Guingamp", "EA Guingamp": "Guingamp",
    "Le Havre": "Le Havre",
    "Lens": "Lens", "RC Lens": "Lens",
    "Lille": "Lille", "Lille OSC": "Lille",
    "Lorient": "Lorient",
    "Lyon": "Lyon", "Olympique Lyonnais": "Lyon",
    "Marseille": "Marseille", "Olympique Marseille": "Marseille", "Olympique de Marseille": "Marseille",
    "Metz": "Metz",
    "Monaco": "Monaco", "AS Monaco": "Monaco",
    "Montpellier": "Montpellier",
    "Nancy": "Nancy",
    "Nantes": "Nantes", "FC Nantes": "Nantes",
    "Nice": "Nice", "OGC Nice": "Nice",
    "Nimes": "Nimes",
    "Paris Saint Germain": "Paris SG", "Paris Saint Germain FC": "Paris SG", "Paris SG": "Paris SG",
    "Reims": "Reims", "Stade Reims": "Reims", "Stade de Reims": "Reims",
    "Rennes": "Rennes", "Stade Rennais": "Rennes",
    "Saint Etienne": "St Etienne", "AS Saint Etienne": "St Etienne",
    "Strasbourg": "Strasbourg", "RC Strasbourg Alsace": "Strasbourg",
    "Toulouse": "Toulouse", "Toulouse FC": "Toulouse",
    "Troyes": "Troyes",
})

_clubes_por_temporada = None


def _carregar():
    global _clubes_por_temporada
    if _clubes_por_temporada is None:
        _clubes_por_temporada = {}
        with open(ARQ_PARTIDAS, encoding="utf-8-sig", newline="") as f:
            for linha in csv.DictReader(f):
                _clubes_por_temporada[(linha["temporada"], linha["clube"])] = linha["liga"]
    return _clubes_por_temporada


def clube_da_liga(nome, temporada, pais=None):
    """Devolve (clube_padronizado, liga) se `nome` for um clube da Premier League
    ou da Ligue 1 NAQUELA temporada; senao devolve (None, None).
    `pais` ('ing' ou 'fra') restringe o dicionario quando a fonte informa o pais."""
    chave = normalizar(nome)
    tabelas = []
    if pais in (None, "ing"):
        tabelas.append(("Premier League", PL))
    if pais in (None, "fra"):
        tabelas.append(("Ligue 1", L1))
    clubes = _carregar()
    for liga, tab in tabelas:
        padrao = tab.get(chave)
        if padrao and clubes.get((temporada, padrao)) == liga:
            return padrao, liga
    return None, None
