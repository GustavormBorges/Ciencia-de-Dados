"""Gera a base de partidas das competicoes europeias (Champions League, Europa League
e Conference League, incluindo qualificatorias) dos clubes da Premier League e da
Ligue 1, de 2015/16 a 2024/25.

Fonte principal: RSSSF (rsssf.org/ec/ecAAAAAA.html), uma pagina por temporada.
Conferencia: totais por fase conferidos com o formato oficial de cada edicao e, para
a fase principal, com o OpenFootball (feita na construcao; ver README).
A Supercopa da UEFA nao entra (fora do escopo).

Entradas : ../fontes-europa-franca/rsssf/ec*.html  e  data/excecoes/excecoes_europa.csv
Saidas   : data/processed/partidas_europa.csv
           data/processed/partidas_europa_por_clube.csv
           data/processed/auditoria_europa.csv
"""
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

import leitor_rsssf_europa as leitor
import nomes_clubes as nomes

RAIZ = Path(__file__).resolve().parents[2]
PASTA_FONTES = RAIZ.parent / "fontes-europa-franca" / "rsssf"
PASTA_SAIDA = RAIZ / "data" / "processed"
ARQ_EXCECOES = RAIZ / "data" / "excecoes" / "excecoes_europa.csv"

FASE_PRINCIPAL = re.compile(r"Group|League Stage|Intermediate|1/8|Quarter|Semi|^Final")

# partidas da fase principal por edicao (grupos/fase de liga + mata-mata), conforme o
# formato oficial; 2019/20 teve quartas e semis em jogo unico (covid) e 2021/22 teve
# dois confrontos da Europa League decididos sem jogo (clubes russos excluidos)
ESPERADO = {
    "Champions League": {**{a: 125 for a in range(2015, 2024)}, 2019: 119, 2024: 189},
    "Europa League": {2015: 205, 2016: 205, 2017: 205, 2018: 205, 2019: 197, 2020: 205,
                      2021: 139, 2022: 141, 2023: 141, 2024: 189},
    "Conference League": {2021: 141, 2022: 141, 2023: 141, 2024: 153},
}
COLUNAS_COMP = {"Champions League": "partidas_champions",
                "Europa League": "partidas_europa_league",
                "Conference League": "partidas_conference_league"}


def carregar_excecoes():
    exc = {}
    with open(ARQ_EXCECOES, encoding="utf-8-sig", newline="") as f:
        for l in csv.DictReader(f, delimiter=";"):
            exc[(l["temporada"], l["competicao"], l["fase"], l["mandante"], l["visitante"])] = l
    return exc


def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    excecoes = carregar_excecoes()
    aplicadas = set()
    saida, auditoria = [], []
    por_clube = defaultdict(Counter)

    for ano in range(2015, 2025):
        arq = PASTA_FONTES / f"ec{ano}{str(ano + 1)[-2:]}.html"
        if not arq.exists():
            raise FileNotFoundError(f"Fonte nao encontrada: {arq}")
        partidas = leitor.ler_europa(str(arq))
        temporada = f"{ano}/{ano + 1}"
        lidas = Counter()
        principais = Counter()
        incons = 0

        for p in partidas:
            p["temporada"] = temporada
            fase = (p["fase"] or "").strip()
            chave = (temporada, p["competicao"], p["fase"], p["mandante"], p["visitante"])
            ex = excecoes.get(chave)
            if ex:
                p["mandante"], p["visitante"] = ex["mandante_correto"], ex["visitante_correto"]
                p["gols_mandante"] = int(ex["gols_mandante_correto"])
                p["gols_visitante"] = int(ex["gols_visitante_correto"])
                aplicadas.add(chave)
            lidas[p["competicao"]] += 1
            etapa = "fase principal" if FASE_PRINCIPAL.search(fase) else "qualificatoria"
            if etapa == "fase principal":
                principais[p["competicao"]] += 1

            clube_m, liga_m = nomes.clube_da_liga(p["mandante"], temporada)
            clube_v, liga_v = nomes.clube_da_liga(p["visitante"], temporada)
            if not (clube_m or clube_v):
                continue
            if p.get("agregado_confere") is False and ano <= 2023:
                incons += 1
            fase_curta = re.sub(r"\s*\(.*", "", fase)
            saida.append({
                "temporada": temporada, "competicao": p["competicao"], "fase": fase_curta, "etapa": etapa,
                "mandante": clube_m or p["mandante"], "visitante": clube_v or p["visitante"],
                "gols_mandante": p["gols_mandante"], "gols_visitante": p["gols_visitante"],
                "fonte": "RSSSF", "status_competicao": "normal", "contar_como_partida": "sim",
                "mandante_na_liga": liga_m or "", "visitante_na_liga": liga_v or "",
            })
            for clube in (clube_m, clube_v):
                if clube:
                    por_clube[(temporada, clube)][p["competicao"]] += 1
                    por_clube[(temporada, clube)][etapa] += 1

        for comp, col in COLUNAS_COMP.items():
            if lidas[comp] == 0 and ano < 2021 and comp == "Conference League":
                continue
            esperado = ESPERADO[comp].get(ano)
            auditoria.append({
                "temporada": temporada, "competicao": comp,
                "partidas_lidas": lidas[comp],
                "fase_principal_lida": principais[comp],
                "fase_principal_esperada": esperado if esperado is not None else "",
                "confere_formato": "sim" if esperado == principais[comp] else "NAO",
                "fonte_principal": "RSSSF",
            })
        if incons:
            print(f"  aviso {temporada}: {incons} partidas de clubes das ligas com agregado divergente na fonte")

    faltantes = set(excecoes) - aplicadas
    if faltantes:
        raise ValueError(f"Excecoes nao aplicadas: {faltantes}")

    campos = ["temporada", "competicao", "fase", "etapa", "mandante", "visitante", "gols_mandante",
              "gols_visitante", "fonte", "status_competicao", "contar_como_partida",
              "mandante_na_liga", "visitante_na_liga"]
    with open(PASTA_SAIDA / "partidas_europa.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(saida)

    linhas = []
    for (temporada, clube), c in sorted(por_clube.items()):
        linhas.append({
            "temporada": temporada, "clube": clube,
            "partidas_champions": c["Champions League"],
            "partidas_europa_league": c["Europa League"],
            "partidas_conference_league": c["Conference League"],
            "partidas_europa": c["Champions League"] + c["Europa League"] + c["Conference League"],
            "partidas_europa_qualificatorias": c["qualificatoria"],
        })
    campos2 = ["temporada", "clube", "partidas_champions", "partidas_europa_league",
               "partidas_conference_league", "partidas_europa", "partidas_europa_qualificatorias"]
    with open(PASTA_SAIDA / "partidas_europa_por_clube.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos2)
        w.writeheader()
        w.writerows(linhas)

    with open(PASTA_SAIDA / "auditoria_europa.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(auditoria[0]))
        w.writeheader()
        w.writerows(auditoria)

    nao = [a for a in auditoria if a["confere_formato"] != "sim"]
    print("GERACAO CONCLUIDA")
    print("Partidas de clubes das ligas:", len(saida))
    print("Clubes-temporada com jogos europeus:", len(linhas))
    print("Excecoes aplicadas:", len(aplicadas))
    print("Edicoes que NAO conferem com o formato:", nao if nao else "nenhuma")


if __name__ == "__main__":
    main()
