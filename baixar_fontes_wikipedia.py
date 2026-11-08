import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "fontes-europa-franca" / "wikipedia"
DESTINO.mkdir(parents=True, exist_ok=True)


def baixar(titulo, arquivo):
    url = ("https://en.wikipedia.org/w/index.php?title="
           + urllib.parse.quote(titulo.replace(" ", "_")) + "&action=raw")
    req = urllib.request.Request(
        url, headers={"User-Agent": "projeto-academico-ICD-UFPB/1.0 (trabalho de faculdade)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            (DESTINO / arquivo).write_bytes(r.read())
        return "OK"
    except urllib.error.HTTPError as e:
        return f"erro {e.code}"
    except Exception as e:
        return f"falhou: {e}"


for ano in range(2015, 2025):
    fim = str(ano + 1)[-2:]
    paginas = [
        (f"{ano}\u2013{fim} Coupe de France", f"coupe_de_france_{ano}_{fim}.txt"),
        (f"{ano} Troph\u00e9e des Champions", f"trophee_{ano}.txt"),
    ]
    for titulo, arquivo in paginas:
        print(f"{arquivo:32} {baixar(titulo, arquivo)}")
        time.sleep(1.5)

print("\nPasta:", DESTINO)