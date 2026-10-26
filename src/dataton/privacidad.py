"""verificar-privacidad: busca posibles datos personales en nombres de columna y en valores.

Informa archivo, columna, tipo de patrón y cantidad. NUNCA muestra ni guarda el valor encontrado.

Cuidado con los falsos positivos: los códigos SIE tienen 8 dígitos y algunos empiezan con 6 o 7,
igual que muchos celulares. Por eso:
- las columnas de código (por su nombre) no se revisan con los patrones de teléfono ni de cédula;
- en una columna donde casi todos los valores son números enteros, un número de 8 dígitos solo
  cuenta como teléfono si el nombre de la columna sugiere un contacto;
- en columnas de texto, un número de 8 dígitos cuenta como teléfono solo si va junto a una
  palabra de contacto (cel, telf, teléfono, whatsapp…) o el nombre de la columna lo sugiere.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from dataton import tablas

COLUMNA_SOSPECHOSA = re.compile(
    r"(?i)\b(nombres?|apellidos?|tel[eé]fonos?|telf|celular(es)?|cel|correos?|e-?mail|c[eé]dula|carnet|\bci\b|"
    r"docentes?|director(a|es)?|fecha.{0,4}nac|nacimiento)\b")
# Columnas cuyo nombre indica que el valor es una persona o un contacto (gravedad alta).
COLUMNA_ALTA = re.compile(r"(?i)(apellido|tel[eé]fono|telf|celular|correo|e-?mail|c[eé]dula|carnet|^ci$|nacimiento|fecha.{0,4}nac)")
COLUMNA_CODIGO = re.compile(r"(?i)(c[oó]d|codigo|sie\b|\bid\b|^id_|_id$|ocid|ubigeo|n[°ºo]\.?\s|nro|n[uú]mero de (registro|infra))")
CONTEXTO_CONTACTO = re.compile(r"(?i)(cel|telf|tel[eé]fono|whats|contacto|llamar|fono)")

CORREO = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
TELEFONO = re.compile(r"(?<![\d.])[67]\d{7}(?![\d.])")
CEDULA = re.compile(r"(?<!\d)\d{5,9}\s*-?\s*(LP|CB|SC|OR|PT|CH|TJ|BE|PD)\b")
FECHA = re.compile(r"\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}-\d{2}-\d{2})\b")

EXTENSIONES = {".csv", ".geojson", ".xlsx"}
EXCLUIR = {".git", ".venv", "__pycache__", "node_modules"}


@dataclass
class Hallazgo:
    archivo: str
    columna: str
    tipo: str
    cantidad: int
    gravedad: str  # alta | revisar

    def texto(self) -> str:
        return f"[{self.gravedad}] {self.archivo} | columna {self.columna!r} | {self.tipo} | {self.cantidad} celda(s)"


def _mayoria_entera(valores: list[str]) -> bool:
    llenos = [v.strip() for v in valores if v.strip()]
    return bool(llenos) and sum(1 for v in llenos if re.fullmatch(r"-?\d+", v)) / len(llenos) >= 0.9


def revisar_tabla(t: tablas.Tabla, rel: str) -> list[Hallazgo]:
    hallazgos = []
    for i, nombre in enumerate(t.encabezado):
        col = nombre or f"(columna {i + 1} sin encabezado)"
        if COLUMNA_SOSPECHOSA.search(nombre or ""):
            hallazgos.append(Hallazgo(rel, col, "nombre de columna sospechoso", 0,
                                      "alta" if COLUMNA_ALTA.search(nombre) else "revisar"))
        valores = [f[i] if i < len(f) else "" for f in t.filas]
        es_codigo = bool(COLUMNA_CODIGO.search(nombre or ""))
        contacto_col = bool(CONTEXTO_CONTACTO.search(nombre or ""))
        entera = _mayoria_entera(valores)
        cuentas = {"correo electrónico": 0, "teléfono": 0, "cédula de identidad": 0, "fecha (posible nacimiento)": 0}
        for v in valores:
            if not v:
                continue
            if CORREO.search(v):
                cuentas["correo electrónico"] += 1
            if not es_codigo:
                if TELEFONO.search(v) and (contacto_col or (not entera and CONTEXTO_CONTACTO.search(v))):
                    cuentas["teléfono"] += 1
                if CEDULA.search(v):
                    cuentas["cédula de identidad"] += 1
            if re.search(r"(?i)nac", nombre or "") and FECHA.search(v):
                cuentas["fecha (posible nacimiento)"] += 1
        for tipo, n in cuentas.items():
            if n:
                hallazgos.append(Hallazgo(rel, col, tipo, n, "alta"))
    return hallazgos


ARCHIVO_IGNORAR = ".dataton-privacidad-ignorar"


def ignorados(ruta: Path) -> list[str]:
    """Rutas (relativas a la carpeta revisada) que se excluyen de una revisión de carpeta completa.
    Se listan, una por línea, en .dataton-privacidad-ignorar. Sirve para los datos de prueba que
    contienen datos personales FICTICIOS a propósito."""
    archivo = ruta / ARCHIVO_IGNORAR
    if not archivo.is_file():
        return []
    return [l.strip().rstrip("/") for l in archivo.read_text(encoding="utf-8").splitlines()
            if l.strip() and not l.startswith("#")]


def archivos(ruta: Path) -> list[Path]:
    if ruta.is_file():
        return [ruta]
    fuera = ignorados(ruta)
    return sorted(p for p in ruta.rglob("*") if p.is_file() and p.suffix in EXTENSIONES
                  and not any(x in EXCLUIR for x in p.relative_to(ruta).parts)
                  and not any(p.relative_to(ruta).as_posix().startswith(i + "/") or p.relative_to(ruta).as_posix() == i for i in fuera))


def verificar(ruta: Path) -> list[Hallazgo]:
    base = ruta if ruta.is_dir() else ruta.parent
    hallazgos: list[Hallazgo] = []
    for archivo in archivos(ruta):
        rel = archivo.relative_to(base).as_posix()
        try:
            for t in tablas.leer(archivo):
                nombre = rel + (t.nombre[t.nombre.index("#"):] if "#" in t.nombre else "")
                hallazgos += revisar_tabla(t, nombre)
        except Exception as e:  # un archivo ilegible no detiene la revisión, pero se informa
            hallazgos.append(Hallazgo(rel, "-", f"no se pudo leer ({type(e).__name__})", 0, "revisar"))
        if archivo.suffix == ".xlsx":
            for campo in tablas.metadatos_autor_xlsx(archivo):
                hallazgos.append(Hallazgo(rel, f"metadatos ({campo})", "metadatos de autor", 1, "alta"))
    return hallazgos
