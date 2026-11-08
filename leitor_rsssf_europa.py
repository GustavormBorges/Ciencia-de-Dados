"""Leitor das paginas da RSSSF sobre as competicoes da UEFA (ecAAAAAA.html).

Le Champions League, Europa League e Conference League, jogo a jogo, incluindo
qualificatorias. Os confrontos de ida e volta aparecem em uma unica linha na fonte
(placar da ida, da volta e agregado) e viram duas partidas. A Supercopa da UEFA e
ignorada. Arquivos de 2023/24 em diante estao em UTF-16.
"""
import re, html
from pathlib import Path

COMP = re.compile(r'^\s*(UEFA Champions League|Europa League|Conference League)\s+(20\d\d)[-/](\d\d)\s*$')
FASE = re.compile(r'^\s*(Preliminary Round|(?:First|Second|Third)? ?Qualifying (?:Phase|Round) ?\d?|Qualifying Round|Intermediate Round|First Round|Play-?offs?|Knockout Round Play-?offs?|Group Phase|Group Stage|League Phase|League Stage|Knockout Phase Play-?offs?|1/16 Finals?|1/8 Finals?|Round of \d+|Quarter-?[Ff]inals?|Semi-?[Ff]inals?|Final)\b')
DUAS = re.compile(r'^(?P<a>\S.*?)(?:\s+|(?<=\)))(?P<ca>[A-Z][A-Za-z]{2})\s{2,}(?P<b>\S.*?)(?:\s+|(?<=\)))(?P<cb>[A-Z][A-Za-z]{2})\s+(?P<r>\d+-\d+.*)$')
GRUPO = re.compile(r'^\s*([A-Z][a-z]{2})\s+(\d+):\s+(?P<a>.+?)\s+\([\d-]+\)\s+(?P<ga>\d+)\s+(?P<b>.+?)\s+\([\d-]+\)\s+(?P<gb>\d+)\s*[a-z*]?\s*$')
PLACAR = re.compile(r'\*?(\d+)-(\d+)')

def ler_texto(caminho):
    bruto = Path(caminho).read_bytes()
    if bruto[:2] in (b'\xff\xfe', b'\xfe\xff'):
        texto = bruto.decode('utf-16')
    else:
        try:
            texto = bruto.decode('utf-8')
        except UnicodeDecodeError:
            texto = bruto.decode('cp1252', errors='replace')
    texto = re.sub(r'<[^>]+>', '', texto)
    return html.unescape(texto)

def ler_europa(caminho):
    partidas = []
    comp = None
    fase = None
    finais = {}
    for linha in ler_texto(caminho).splitlines():
        if '|' not in linha:
            m = COMP.match(linha)
            if m:
                nome = {'UEFA Champions League': 'Champions League', 'Europa League': 'Europa League',
                        'Conference League': 'Conference League'}[m.group(1)]
                comp = (nome, f"{m.group(2)}/{int(m.group(2)) + 1}")
                fase = None
                continue
        if re.match(r'^\s*Super Cup\b', linha) and '|' not in linha:
            comp = ('Supercopa', '')
            continue
        if comp is None:
            continue
        mf = FASE.match(linha)
        if mf and re.match(r'Final\b', linha.strip()) and not (fase or '').startswith('Preliminary'):
            finais[comp] = finais.get(comp, 0) + 1
            if finais[comp] > 1:
                comp = (comp[0] + ' (Supercopa)', comp[1])   # Supercopa da UEFA: fora do escopo
                finais[comp] = 1
        if mf and not DUAS.match(linha):
            novo = linha.strip()
            if fase and fase.startswith('Preliminary') and re.match(r'(Semi|Final)', novo):
                continue
            fase = novo
            continue
        g = GRUPO.match(linha)
        if g:
            partidas.append(dict(competicao=comp[0], temporada=comp[1], fase=fase or 'Group',
                                 mandante=g['a'].strip(), visitante=g['b'].strip(),
                                 gols_mandante=int(g['ga']), gols_visitante=int(g['gb'])))
            continue
        d = DUAS.match(linha)
        if d:
            placares = PLACAR.findall(d['r'])
            a, b = d['a'].strip(), d['b'].strip()
            # duas pernas: ida (a em casa), volta (b em casa); jogo unico: um placar so
            if len(placares) >= 3:
                (g1a, g1b), (g2a, g2b), (aa, ab) = map(lambda t: tuple(map(int, t)), placares[:3])
                confere = (g1a + g2a == aa and g1b + g2b == ab)
                partidas.append(dict(competicao=comp[0], temporada=comp[1], fase=fase, mandante=a, visitante=b,
                                     gols_mandante=g1a, gols_visitante=g1b, agregado_confere=confere))
                partidas.append(dict(competicao=comp[0], temporada=comp[1], fase=fase, mandante=b, visitante=a,
                                     gols_mandante=g2b, gols_visitante=g2a, agregado_confere=confere))
            else:
                p = tuple(map(int, placares[0]))
                partidas.append(dict(competicao=comp[0], temporada=comp[1], fase=fase, mandante=a, visitante=b,
                                     gols_mandante=p[0], gols_visitante=p[1]))
    return [p for p in partidas if not p['competicao'].startswith('Supercopa') and 'Supercopa' not in p['competicao']]
