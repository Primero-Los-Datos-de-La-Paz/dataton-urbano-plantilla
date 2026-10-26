"""Genera el derivado agregado de demostración (código y total por escuela)."""
import csv
from pathlib import Path

paquete = Path(__file__).resolve().parents[1]
with (paquete / "data" / "interim" / "escuelas.csv").open(encoding="utf-8", newline="") as fh:
    filas = list(csv.DictReader(fh))
(paquete / "derivado").mkdir(exist_ok=True)
with (paquete / "derivado" / "agregado.csv").open("w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n")
    w.writerow(["codigo", "total"])
    for f in filas:
        w.writerow([f["codigo"], f["total"]])
