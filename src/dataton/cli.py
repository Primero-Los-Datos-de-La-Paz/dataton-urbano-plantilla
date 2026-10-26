"""Interfaz de línea de comandos: python -m dataton <comando>."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from dataton import __version__, edicion, generar

# Lo que no se copia al crear una edición nueva desde la plantilla.
NO_COPIAR = shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", "*.egg-info", ".DS_Store")


def _informar(errores: list[str], pendientes: list[str]) -> None:
    for e in errores:
        print(f"ERROR: {e}", file=sys.stderr)
    if pendientes:
        print(f"Campos por definir en edicion.yml ({len(pendientes)}):")
        for p in pendientes:
            print(f"  - {p}")


def cmd_init_edicion(args: argparse.Namespace) -> int:
    origen = Path(args.plantilla).resolve()
    destino = Path(args.destino).resolve()
    ruta_ed = Path(args.edicion).resolve()

    ed = edicion.cargar(ruta_ed)
    errores, pendientes = edicion.validar(ed)
    _informar(errores, pendientes)
    if errores:
        return 1
    if destino.exists() and any(destino.iterdir()):
        print(f"ERROR: la carpeta de destino {destino} ya existe y no está vacía.", file=sys.stderr)
        return 1
    if destino == origen or origen in destino.parents:
        print("ERROR: el destino no puede estar dentro de la plantilla.", file=sys.stderr)
        return 1

    shutil.copytree(origen, destino, ignore=NO_COPIAR, dirs_exist_ok=True)
    shutil.copyfile(ruta_ed, destino / edicion.RUTA_EDICION)
    cambiados = generar.regenerar(destino, ed)
    print(f"Edición creada en {destino}")
    print(f"Archivos generados desde edicion.yml: {len(cambiados)}")
    return 0


def cmd_regenerar(args: argparse.Namespace) -> int:
    raiz = Path(args.raiz).resolve()
    ed = edicion.cargar(raiz / edicion.RUTA_EDICION)
    errores, pendientes = edicion.validar(ed)
    _informar(errores, pendientes)
    if errores:
        return 1
    cambiados = generar.regenerar(raiz, ed, solo_comprobar=args.comprobar)
    if args.comprobar:
        if cambiados:
            print("Estos archivos no están al día con edicion.yml:")
            for r in cambiados:
                print(f"  - {r.relative_to(raiz).as_posix()}")
            return 1
        print("OK: todos los archivos están al día con edicion.yml.")
        return 0
    print(f"Archivos actualizados: {len(cambiados)}")
    for r in cambiados:
        print(f"  - {r.relative_to(raiz).as_posix()}")
    return 0


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="python -m dataton", description="Herramientas del datatón urbano.")
    p.add_argument("--version", action="version", version=f"dataton {__version__}")
    sub = p.add_subparsers(dest="comando", required=True)

    pi = sub.add_parser("init-edicion", help="Crea una edición nueva a partir de la plantilla y de un edicion.yml.")
    pi.add_argument("--edicion", required=True, help="Ruta al edicion.yml de la nueva edición.")
    pi.add_argument("--destino", required=True, help="Carpeta nueva donde se creará la edición.")
    pi.add_argument("--plantilla", default=".", help="Carpeta de la plantilla (por defecto, la actual).")
    pi.set_defaults(func=cmd_init_edicion)

    pr = sub.add_parser("regenerar", help="Actualiza los textos generados a partir de edicion/edicion.yml.")
    pr.add_argument("--raiz", default=".", help="Carpeta del repositorio (por defecto, la actual).")
    pr.add_argument("--comprobar", action="store_true", help="Solo comprueba; no escribe nada.")
    pr.set_defaults(func=cmd_regenerar)
    return p


def main(argv: list[str] | None = None) -> int:
    args = construir_parser().parse_args(argv)
    try:
        return args.func(args)
    except (edicion.ErrorEdicion, generar.ErrorBloque) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
