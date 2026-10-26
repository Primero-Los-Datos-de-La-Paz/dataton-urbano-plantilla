"""Interfaz de línea de comandos: python -m dataton <comando>."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

from dataton import __version__, edicion, generar
from dataton import validar as m_validar

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


def _rutas(args: argparse.Namespace) -> list[Path]:
    rutas = [Path(r) for r in args.rutas]
    if getattr(args, "todos", False):
        rutas += m_validar.paquetes_de(Path(args.raiz))
    if not rutas:
        raise SystemExit("Indica al menos una ruta, o --todos.")
    return rutas


def _guardar(datos: dict, destino: str | None) -> None:
    if destino:
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        Path(destino).write_text(json.dumps(datos, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"Guardado en {destino}")


def cmd_validar(args: argparse.Namespace) -> int:
    if args.todos and not args.rutas and not m_validar.paquetes_de(Path(args.raiz)):
        print("No hay paquetes que validar en paquetes/ (se omiten las carpetas que empiezan con '_').")
        return 0
    codigo = 0
    for ruta in _rutas(args):
        res = m_validar.validar(ruta)
        print(f"{'OK   ' if res.ok else 'ERROR'} {res.tipo} {ruta}")
        for e in res.errores:
            print(f"   error: {e}")
        for a in res.advertencias:
            print(f"   aviso: {a}")
        codigo = codigo or (0 if res.ok else 1)
    return codigo


def cmd_scorecard(args: argparse.Namespace) -> int:
    from dataton import scorecard
    sc = scorecard.scorecard(Path(args.ruta), Path(args.reglas) if args.reglas else None)
    print(scorecard.resumen(sc))
    _guardar(sc, args.guardar)
    return 0


def cmd_nivel(args: argparse.Namespace) -> int:
    from dataton import nivel
    paq = Path(args.ruta)
    escala = Path(args.escala) if args.escala else nivel.buscar_escala(paq)
    if not escala or not escala.is_file():
        print("ERROR: no se encontró evaluacion/escala-preparacion-0-7.yml. Indica su ruta con --escala.", file=sys.stderr)
        return 1
    r = nivel.evaluar(paq, escala, Path(args.reglas) if args.reglas else None)
    print(nivel.resumen(r))
    _guardar(r, args.guardar)
    return 0


def cmd_reproducir(args: argparse.Namespace) -> int:
    from dataton import reproducir
    res = reproducir.reproducir(Path(args.ruta), ejecutar=args.ejecutar)
    print(reproducir.resumen(res))
    if not args.ejecutar:
        return 1 if res.errores else 0
    return 0 if res.ok else 1


def cmd_privacidad(args: argparse.Namespace) -> int:
    from dataton import privacidad
    graves = 0
    for ruta in [Path(r) for r in args.rutas]:
        hallazgos = privacidad.verificar(ruta)
        print(f"Revisión de privacidad de {ruta}: {len(hallazgos)} hallazgo(s). Nunca se muestran los valores.")
        for h in hallazgos:
            print(f"  {h.texto()}")
        graves += sum(1 for h in hallazgos if h.gravedad == "alta")
    if graves:
        print(f"ERROR: {graves} hallazgo(s) de gravedad alta. Revisa los archivos indicados (sin copiar los valores).")
        return 1
    print("OK: sin hallazgos de gravedad alta.")
    return 0


def cmd_liberar(args: argparse.Namespace) -> int:
    from dataton import liberar
    ev, mensajes = liberar.liberar(Path(args.ruta), Path(args.destino), ejecutar=args.ejecutar)
    print("\n".join(mensajes))
    return 0 if ev.aprobada else 1


def cmd_demo(args: argparse.Namespace) -> int:
    from dataton import demo
    fallas = demo.ejecutar()
    if fallas:
        print("\nFALLAS:")
        for f in fallas:
            print(f"  - {f}")
        return 1
    print("\nOK")
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

    pv = sub.add_parser("validar", help="Valida datapackage.json, sumas y estructura de un paquete o de una entrega.")
    pv.add_argument("rutas", nargs="*", help="Carpetas de paquetes o de repositorios de entrega.")
    pv.add_argument("--todos", action="store_true", help="Valida todos los paquetes de paquetes/ (omite los que empiezan con '_').")
    pv.add_argument("--raiz", default=".", help="Raíz del repositorio para --todos.")
    pv.set_defaults(func=cmd_validar)

    ps = sub.add_parser("scorecard", help="Mide las dimensiones de calidad con las reglas de reglas-calidad.yml.")
    ps.add_argument("ruta", help="Carpeta del paquete.")
    ps.add_argument("--reglas", help="Archivo de reglas (por defecto, reglas-calidad.yml del paquete).")
    ps.add_argument("--guardar", help="Guarda el resultado en este archivo JSON.")
    ps.set_defaults(func=cmd_scorecard)

    pn = sub.add_parser("nivel", help="Propone un nivel de la escala 0-7, con los criterios cumplidos y faltantes.")
    pn.add_argument("ruta", help="Carpeta del paquete.")
    pn.add_argument("--escala", help="Ruta de escala-preparacion-0-7.yml (por defecto, se busca evaluacion/).")
    pn.add_argument("--reglas", help="Archivo de reglas (por defecto, reglas-calidad.yml del paquete).")
    pn.add_argument("--guardar", help="Guarda el resultado en este archivo JSON.")
    pn.set_defaults(func=cmd_nivel)

    pp = sub.add_parser("reproducir", help="Ejecuta los scripts en una copia temporal y compara las sumas declaradas.")
    pp.add_argument("ruta", help="Carpeta del paquete o del repositorio de entrega.")
    pp.add_argument("--ejecutar", action="store_true", help="Ejecuta los scripts (sin esta opción solo muestra el plan).")
    pp.set_defaults(func=cmd_reproducir)

    pq = sub.add_parser("verificar-privacidad", help="Busca posibles datos personales. Informa archivo, columna y tipo; nunca el valor.")
    pq.add_argument("rutas", nargs="+", help="Archivos o carpetas.")
    pq.set_defaults(func=cmd_privacidad)

    pl = sub.add_parser("liberar", help="Publica un derivado solo si liberacion.yml está aprobado y la privacidad pasa.")
    pl.add_argument("ruta", help="Carpeta del paquete interno.")
    pl.add_argument("--destino", required=True, help="Carpeta local del repositorio público (clon de git).")
    pl.add_argument("--ejecutar", action="store_true", help="Prepara la rama (sin esta opción, solo simulación).")
    pl.set_defaults(func=cmd_liberar)

    pd = sub.add_parser("demo", help="Ejecuta todo sobre datos sintéticos y termina con OK o la lista de fallas.")
    pd.set_defaults(func=cmd_demo)
    return p


def main(argv: list[str] | None = None) -> int:
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="replace")  # consolas de Windows sin UTF-8
    args = construir_parser().parse_args(argv)
    try:
        return args.func(args)
    except (edicion.ErrorEdicion, generar.ErrorBloque) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
