"""Gera a base de partidas das copas francesas dos clubes da Ligue 1, de 2015/16 a 2024/25:
Coupe de France, Coupe de la Ligue (extinta apos 2019/20) e Trophee des Champions.

Fontes:
  - RSSSF  (fran{ano_final}.html): Coupe de France e Coupe de la Ligue.
    Nas temporadas 2020/21 a 2024/25 a pagina da Coupe de France so comeca nos
    16-avos de final, entao faltam os 32-avos, que e a fase de estreia da Ligue 1.
  - Wikipedia (wikitexto): Coupe de France (32-avos em diante) e Trophee des Champions.
    Nas temporadas em que as duas fontes cobrem a mesma fase, os resultados sao
    comparados (divergencias_franca.csv). Onde so a Wikipedia cobre (32-avos de
    2020/21 a 2024/25), ela e a fonte usada.

Entradas : ../fontes-europa-franca/rsssf/fran*.html
           ../fontes-europa-franca/wikipedia/*.txt
Saidas   : data/processed/partidas_copas_franca.csv
           data/processed/partidas_copas_franca_por_clube.csv
           data/processed/auditoria_copas_franca.csv
           data/processed/divergencias_franca.csv
"""
import csv
from collections import Counter, defaultdict
from pathlib import Path

import leitor_copas_franca as leitor
import nomes_clubes as nomes

RAIZ = Path(__file__).resolve().parents[2]
FONTES = RAIZ.parent / "fontes-europa-franca"
PASTA_SAIDA = RAIZ / "data" / "processed"

COLUNAS = {"Coupe de France": "partidas_coupe_de_france",
           "Coupe de la Ligue": "partidas_coupe_de_la_ligue",
           "Trophée des Champions": "partidas_trophee_des_champions"}


def visao_por_clube(partidas, temporada):
    """(clube da Ligue 1, fase) -> lista de (gols pro, gols contra); so Coupe de France."""
    v = defaultdict(list)
    for p in partidas:
        if p["competicao"] != "Coupe de France":
            continue
        for a, b, ga, gb in ((p["mandante"], p["visitante"], p["gols_mandante"], p["gols_visitante"]),
                             (p["visitante"], p["mandante"], p["gols_visitante"], p["gols_mandante"])):
            clube, _ = nomes.clube_da_liga(a, temporada, "fra")
            if clube:
                v[(clube, p["fase"])].append((ga, gb, b))
    return v


def main():
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    saida, auditoria, divergencias = [], [], []
    por_clube = defaultdict(Counter)

    for ano in range(2015, 2025):
        temporada = f"{ano}/{ano + 1}"
        arq_rsssf = FONTES / "rsssf" / f"fran{ano + 1}.html"
        arq_wiki = FONTES / "wikipedia" / f"coupe_de_france_{ano}_{str(ano + 1)[-2:]}.txt"
        arq_trof = FONTES / "wikipedia" / f"trophee_{ano}.txt"
        for a in (arq_rsssf, arq_wiki, arq_trof):
            if not a.exists():
                raise FileNotFoundError(f"Fonte nao encontrada: {a}")

        rsssf = leitor.ler_rsssf_franca(str(arq_rsssf), ano)
        wiki = leitor.ler_wikipedia_copa_franca(str(arq_wiki), ano)
        trofeu = leitor.ler_wikipedia_trophee(str(arq_trof), ano)

        # --- comparacao RSSSF x Wikipedia nas fases que as duas cobrem (Coupe de France)
        fases_rsssf = {p["fase"] for p in rsssf if p["competicao"] == "Coupe de France"}
        vr, vw = visao_por_clube(rsssf, temporada), visao_por_clube(wiki, temporada)
        for chave in sorted(set(vr) | set(vw)):
            clube, fase = chave
            if fase not in fases_rsssf or fase == "final":
                continue
            a = sorted((x[0], x[1]) for x in vr.get(chave, []))
            b = sorted((x[0], x[1]) for x in vw.get(chave, []))
            if a != b:
                divergencias.append({"temporada": temporada, "clube": clube, "fase": fase,
                                     "rsssf": str(vr.get(chave)), "wikipedia": str(vw.get(chave)),
                                     "fonte_escolhida": "RSSSF",
                                     "observacao": "Wikipedia sem placar para esta partida" if any(
                                         x[0] is None for x in vw.get(chave, [])) else "verificar"})

        # --- partidas finais: RSSSF onde existe; Wikipedia nas fases que o RSSSF nao cobre
        partidas = [dict(p, fonte="RSSSF") for p in rsssf]
        for p in wiki:
            if p["fase"] not in fases_rsssf:
                partidas.append(dict(p, fonte="Wikipedia"))
        for p in trofeu:
            partidas.append(dict(p, fonte="Wikipedia"))

        lidas, com_clube = Counter(), Counter()
        clubes_com_jogo = defaultdict(set)
        for p in partidas:
            comp = p["competicao"]
            lidas[comp] += 1
            clube_m, _ = nomes.clube_da_liga(p["mandante"], temporada, "fra")
            clube_v, _ = nomes.clube_da_liga(p["visitante"], temporada, "fra")
            if not (clube_m or clube_v):
                continue
            com_clube[comp] += 1
            saida.append({
                "temporada": temporada, "competicao": comp, "fase": p["fase"], "data": p["data"],
                "mandante": clube_m or p["mandante"], "visitante": clube_v or p["visitante"],
                "gols_mandante": "" if p["gols_mandante"] is None else p["gols_mandante"],
                "gols_visitante": "" if p["gols_visitante"] is None else p["gols_visitante"],
                "fonte": p["fonte"], "status_competicao": p["status_competicao"],
                "contar_como_partida": p["contar_como_partida"], "observacao": p["observacao"],
            })
            if p["contar_como_partida"] == "sim":
                for clube in (clube_m, clube_v):
                    if clube:
                        por_clube[(temporada, clube)][comp] += 1
                        clubes_com_jogo[comp].add(clube)

        na_liga = {c for (t, c), liga in nomes._carregar().items() if t == temporada and liga == "Ligue 1"}
        for comp in COLUNAS:
            if comp == "Coupe de la Ligue" and ano >= 2020:
                continue
            fonte = "Wikipedia" if comp == "Trophée des Champions" else (
                "RSSSF + Wikipedia" if comp == "Coupe de France" else "RSSSF")
            auditoria.append({
                "temporada": temporada, "competicao": comp, "fonte_principal": fonte,
                "partidas_lidas": lidas[comp], "partidas_com_clube_da_liga": com_clube[comp],
                "clubes_ligue1_na_temporada": len(na_liga),
                "clubes_ligue1_com_jogo": len(clubes_com_jogo[comp] & na_liga),
            })

    campos = ["temporada", "competicao", "fase", "data", "mandante", "visitante", "gols_mandante",
              "gols_visitante", "fonte", "status_competicao", "contar_como_partida", "observacao"]
    with open(PASTA_SAIDA / "partidas_copas_franca.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(saida)

    linhas = []
    for (temporada, clube), c in sorted(por_clube.items()):
        linhas.append({"temporada": temporada, "clube": clube,
                       **{col: c[comp] for comp, col in COLUNAS.items()},
                       "partidas_copas_franca": sum(c[comp] for comp in COLUNAS)})
    campos2 = ["temporada", "clube"] + list(COLUNAS.values()) + ["partidas_copas_franca"]
    with open(PASTA_SAIDA / "partidas_copas_franca_por_clube.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos2)
        w.writeheader()
        w.writerows(linhas)

    with open(PASTA_SAIDA / "auditoria_copas_franca.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(auditoria[0]))
        w.writeheader()
        w.writerows(auditoria)

    campos3 = ["temporada", "clube", "fase", "rsssf", "wikipedia", "fonte_escolhida", "observacao"]
    with open(PASTA_SAIDA / "divergencias_franca.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=campos3)
        w.writeheader()
        w.writerows(divergencias)

    print("GERACAO CONCLUIDA")
    print("Partidas de clubes da Ligue 1:", len(saida))
    print("Clubes-temporada com jogos:", len(linhas))
    print("Divergencias entre fontes:", len(divergencias))
    # Coupe de France: todo clube da Ligue 1 estreia nos 32-avos, entao a cobertura tem que ser total
    falhas = [a for a in auditoria
              if a["competicao"] in ("Coupe de France",) and a["clubes_ligue1_com_jogo"] != a["clubes_ligue1_na_temporada"]]
    print("Temporadas em que algum clube da Ligue 1 ficou sem jogo na Coupe de France:", falhas if falhas else "nenhuma")


if __name__ == "__main__":
    main()
