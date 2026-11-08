import time
import urllib.request
import urllib.error
from pathlib import Path

DESTINO = Path(__file__).resolve().parent.parent / "fontes-europa-franca" / "rsssf"
DESTINO.mkdir(parents=True, exist_ok=True)


def baixar(url, arquivo):
    req = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (projeto academico ICD-UFPB)"}
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
    fim = ano + 1
    sufixo = f"{ano}{str(fim)[-2:]}"

    tentativas = [
        (f"https://rsssf.org/ec/ec{sufixo}.html", f"ec{sufixo}.html"),
        (f"https://rsssf.org/tablesf/fran{fim}.html", f"fran{fim}.html"),
        (f"https://rsssf.org/tablesf/fran{fim}.txt", f"fran{fim}.txt"),
    ]

    for url, arquivo in tentativas:
        print(f"{ano}/{fim}  {arquivo:18} {baixar(url, arquivo)}")
        time.sleep(1.5)

print("\nPasta:", DESTINO)