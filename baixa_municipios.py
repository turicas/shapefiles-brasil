"""Baixa CSV com lista da população por município e salva somente o código IBGE e nome (com a grafia original)"""

import csv
import io
from urllib.request import urlopen
from pathlib import Path

url = "https://raw.githubusercontent.com/turicas/censo-ibge/refs/heads/main/data/output/populacao-2025_2025-09-01.csv"
arquivo_final = Path(__file__).parent / "data" / "municipio.csv"
arquivo_final.parent.mkdir(exist_ok=True, parents=True)
response = urlopen(url)
csv_data = response.read().decode("utf-8")
with arquivo_final.open(mode="w") as fobj:
    writer = csv.DictWriter(fobj, fieldnames=["codigo_ibge", "nome"])
    writer.writeheader()
    for row in csv.DictReader(io.StringIO(csv_data)):
        writer.writerow({"codigo_ibge": row["codigo_municipio"], "nome": row["municipio"]})
