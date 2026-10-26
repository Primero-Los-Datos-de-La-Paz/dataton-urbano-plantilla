"""Conversión mecánica de demostración: copia el CSV original a data/interim sin cambiar valores."""
import shutil
from pathlib import Path

paquete = Path(__file__).resolve().parents[1]
(paquete / "data" / "interim").mkdir(parents=True, exist_ok=True)
shutil.copyfile(paquete / "data" / "raw" / "escuelas.csv", paquete / "data" / "interim" / "escuelas.csv")
