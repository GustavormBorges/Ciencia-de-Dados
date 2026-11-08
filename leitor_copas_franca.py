"""Leitores das copas francesas.

- RSSSF (fran{ano_final}.html): Coupe de France e Coupe de la Ligue.
- Wikipedia (wikitexto bruto): Coupe de France (32-avos de final em diante,
  fase em que os clubes da Ligue 1 entram) e Trophee des Champions.
"""
import re
from pathlib import Path

from leitor_rsssf_europa import ler_texto

MESES = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

# nomes das fases padronizados (iguais nas duas fontes)
FASES_RSSSF = [
    (r"Round 9\b", "32-avos"),
    (r"1/16 Finals?", "16-avos"),
    (r"1/8 Finals?", "oitavas"),
    (r"Quarter-?finals?", "quartas"),
    (r"Semi-?finals?", "semifinais"),
    (r"Final\b", "final"),
    (r"Preliminary Round", "fase preliminar"),
    (r"Round (\d)\b", None),   # Coupe de la Ligue: Round 1/2/3
]
FASES_WIKI = {"Round of 64": "32-avos", "Round of 32": "16-avos", "Round of 16": "oitavas",
              "Quarter-finals": "quartas", "Semi-finals": "semifinais"}

PLACAR = re.compile(r"^(?P<a>.+?)\s+(?P<res>\d+-\d+|awd|abd)\s+(?P<b>\S.*?)\s*(?:\[(?P<obs>.*?)\]?)?\s*$")


def _data(mes_dia, ano_inicio):
    m = re.match(r"([A-Z][a-z]{2})\s+(\d+)", mes_dia)
    if not m or m.group(1) not in MESES:
        return ""
    mes = MESES[m.group(1)]
    ano = ano_inicio if mes >= 7 else ano_inicio + 1
    return f"{ano}-{mes:02d}-{int(m.group(2)):02d}"


def ler_rsssf_franca(caminho, ano_inicio):
    """Le a Coupe de France e a Coupe de la Ligue de uma pagina fran{ano}.html."""
    linhas = ler_texto(caminho).replace("\x96", "-").replace("–", "-").splitlines()
    competicao = None
    fase = None
    data = ""
    partidas = []
    for linha in linhas:
        s = linha.strip()
        if re.fullmatch(r"Coupe de la France", s):
            competicao, fase, data = "Coupe de France", None, ""
            continue
        if re.fullmatch(r"Coupe de la Ligue", s):
            competicao, fase, data = "Coupe de la Ligue", None, ""
            continue
        if re.fullmatch(r"(Ligue 2|National|Ligue 1)", s) and competicao:
            if partidas or competicao:
                competicao = None
            continue
        if competicao is None or not s:
            continue
        # cabecalho de fase (pode trazer a data entre colchetes)
        mf = re.match(r"^(Round \d+|Preliminary Round|1/16 Finals?|1/8 Finals?|Quarter-?finals?|Semi-?finals?|Final)\b\s*(?:\[(.*?)\])?\s*$", s, re.I)
        if mf:
            titulo = mf.group(1)
            if competicao == "Coupe de France":
                nome = {"Round 9": "32-avos", "1/16 Finals": "16-avos", "1/8 Finals": "oitavas"}.get(titulo)
                if not nome:
                    t = titulo.lower().replace("-", "")
                    nome = {"quarterfinals": "quartas", "semifinals": "semifinais", "final": "final",
                            "1/16 final": "16-avos", "1/8 final": "oitavas"}.get(t, titulo)
            else:
                t = titulo.lower().replace("-", "")
                nome = {"round 1": "rodada 1", "round 2": "rodada 2", "round 3": "rodada 3",
                        "preliminary round": "fase preliminar", "1/8 finals": "oitavas",
                        "quarterfinals": "quartas", "semifinals": "semifinais", "final": "final"}.get(t, titulo)
            fase = nome
            data = _data(mf.group(2) or "", ano_inicio) if mf.group(2) else data
            continue
        md = re.match(r"^\[([A-Z][a-z]{2}\s+\d+)\]", s)
        if md:
            data = _data(md.group(1), ano_inicio)
            continue
        m = PLACAR.match(s)
        if not m or fase is None:
            continue
        res = m.group("res")
        obs = (m.group("obs") or "").strip()
        if res == "awd":
            gm = gv = None
            status, contar = "nao disputada (W.O.)", "nao"
        elif res == "abd":
            gm = gv = None
            status, contar = "abandonada", "sim"
        else:
            gm, gv = (int(x) for x in res.split("-"))
            status, contar = "normal", "sim"
        partidas.append(dict(competicao=competicao, temporada=f"{ano_inicio}/{ano_inicio + 1}", fase=fase,
                             data=data, mandante=m.group("a").strip(), visitante=m.group("b").strip(),
                             gols_mandante=gm, gols_visitante=gv, observacao=obs,
                             status_competicao=status, contar_como_partida=contar))
    return partidas


# ---------------- Wikipedia ----------------

def _campo(bloco, nome):
    m = re.search(r"^\|\s*" + nome + r"\s*=\s*(.*)$", bloco, re.M)
    return m.group(1).strip() if m else ""


def _nome_time(bruto):
    s = re.sub(r"'''", "", bruto)
    s = re.sub(r"\{\{[^}]*\}\}", "", s)
    s = re.sub(r"<ref.*?(</ref>|/>)", "", s)
    s = re.sub(r"\(\d+\)\s*$", "", s.strip())
    m = re.search(r"\[\[(?:[^\]|]*\|)?([^\]]+)\]\]", s)
    return (m.group(1) if m else s).strip()


def ler_wikipedia_copa_franca(caminho, ano_inicio):
    """Le os jogos da Coupe de France do wikitexto (32-avos em diante)."""
    texto = Path(caminho).read_text(encoding="utf-8")
    partes = re.split(r"^==\s*([^=].*?)\s*==\s*$", texto, flags=re.M)
    partidas = []
    for i in range(1, len(partes), 2):
        fase = FASES_WIKI.get(partes[i].strip())
        if fase is None:
            continue
        for bl in re.split(r"\{\{[Ff]ootball ?box(?: collapsible)?", partes[i + 1])[1:]:
            score = _campo(bl, "score")
            mandante = _nome_time(_campo(bl, "team1"))
            visitante = _nome_time(_campo(bl, "team2"))
            if visitante.lower() == "bye":
                continue
            m = re.match(r"(\d+)\s*[–−-]\s*(\d+)", score)
            if m:
                gm, gv, status, contar = int(m.group(1)), int(m.group(2)), "normal", "sim"
            elif score.lower().startswith("abandoned"):
                gm = gv = None
                status, contar = "abandonada", "sim"
            else:
                gm = gv = None
                status, contar = "sem placar na fonte", "sim"
            partidas.append(dict(competicao="Coupe de France", temporada=f"{ano_inicio}/{ano_inicio + 1}",
                                 fase=fase, data=_campo(bl, "date"), mandante=mandante, visitante=visitante,
                                 gols_mandante=gm, gols_visitante=gv, observacao="",
                                 status_competicao=status, contar_como_partida=contar))
    return partidas


def ler_wikipedia_trophee(caminho, ano):
    """Trophee des Champions: uma unica partida por edicao (infobox)."""
    texto = Path(caminho).read_text(encoding="utf-8")
    t1 = _nome_time(_campo(texto, "team1"))
    t2 = _nome_time(_campo(texto, "team2"))
    g1 = re.search(r"\d+", _campo(texto, "team1score"))
    g2 = re.search(r"\d+", _campo(texto, "team2score"))
    data = re.search(r"\{\{Start date\|(\d+)\|(\d+)\|(\d+)", texto)
    return [dict(competicao="Trophée des Champions", temporada=f"{ano}/{ano + 1}", fase="final",
                 data=f"{data.group(1)}-{int(data.group(2)):02d}-{int(data.group(3)):02d}" if data else "",
                 mandante=t1, visitante=t2,
                 gols_mandante=int(g1.group()) if g1 else None, gols_visitante=int(g2.group()) if g2 else None,
                 observacao="", status_competicao="normal", contar_como_partida="sim")]
