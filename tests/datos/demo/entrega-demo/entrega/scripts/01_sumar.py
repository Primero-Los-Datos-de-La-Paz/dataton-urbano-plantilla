"""Suma las columnas a y b de datos/entrada.csv y escribe salida/resultado.csv."""
import csv
from pathlib import Path

with Path("datos/entrada.csv").open(encoding="utf-8", newline="") as fh:
    filas = list(csv.DictReader(fh))
Path("salida").mkdir(exist_ok=True)
with Path("salida/resultado.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["a", "b", "suma"])
    for f in filas:
        w.writerow([f["a"], f["b"], int(f["a"]) + int(f["b"])])
