"""demo: ejecuta todos los comandos sobre el conjunto sintético de tests/datos/demo y termina con OK o con la lista de fallas.

Trabaja en una carpeta temporal: no modifica nada del repositorio.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import yaml

from dataton import cli, equipos, liberar, nivel, privacidad, recolectar, reproducir, scorecard, validar

RAIZ = Path(__file__).resolve().parents[2]
DEMO = RAIZ / "tests" / "datos" / "demo"


def ejecutar() -> list[str]:
    fallas: list[str] = []

    def comprobar(condicion: bool, mensaje: str) -> None:
        print(("  ok    " if condicion else "  FALLA ") + mensaje)
        if not condicion:
            fallas.append(mensaje)

    if not DEMO.is_dir():
        return [f"No se encuentra el conjunto sintético en {DEMO}. Ejecuta el demo desde el repositorio clonado."]

    with tempfile.TemporaryDirectory(prefix="dataton-demo-") as tmp:
        base = Path(tmp) / "demo"
        shutil.copytree(DEMO, base)
        paq, entrega = base / "paquete-demo", base / "entrega-demo"

        print("validar")
        comprobar(validar.validar(paq).ok, "el paquete sintético es válido")
        comprobar(validar.validar(entrega).ok, "la entrega sintética es válida")
        (paq / "data" / "raw" / "escuelas.csv").write_text("alterado\n", encoding="utf-8")
        comprobar(not validar.validar(paq).ok, "detecta un archivo alterado (suma distinta)")
        shutil.copyfile(DEMO / "paquete-demo" / "data" / "raw" / "escuelas.csv", paq / "data" / "raw" / "escuelas.csv")

        print("scorecard")
        sc = scorecard.scorecard(paq)
        r = sc["recursos"]["data/interim/escuelas.csv"]
        comprobar(r["completitud"]["valor"] == 1.0, "completitud 100 %")
        comprobar(r["validez"]["valor"] == 1.0, "validez 100 %")
        comprobar(r["unicidad"]["valor"] == 1.0, "unicidad 100 %")
        comprobar(r["consistencia"]["valor"] == 1.0, "consistencia 100 %")
        comprobar(r["territorialidad"]["valor"] == 1.0 and r["territorialidad"]["aproximada"], "territorialidad 100 % (aproximada)")
        comprobar(set(sc["revision_humana"]) == {"exactitud", "oportunidad"}, "exactitud y oportunidad quedan para revisión humana")

        print("nivel")
        escala = RAIZ / "evaluacion" / "escala-preparacion-0-7.yml"
        nv = nivel.evaluar(paq, escala)
        comprobar(nv["nivel_propuesto"] == 5, f"nivel propuesto 5 (obtenido {nv['nivel_propuesto']})")

        print("reproducir")
        comprobar(not reproducir.reproducir(paq).ejecutado, "sin --ejecutar no ejecuta nada")
        comprobar(reproducir.reproducir(paq, ejecutar=True).ok, "el paquete se reproduce con sus sumas")
        comprobar(reproducir.reproducir(entrega, ejecutar=True).ok, "la entrega se reproduce con sus sumas")

        print("verificar-privacidad")
        comprobar(not [h for h in privacidad.verificar(paq) if h.gravedad == "alta"], "el paquete sintético no tiene hallazgos graves")
        malos = {h.tipo for h in privacidad.verificar(base / "privacidad-mala") if h.gravedad == "alta"}
        comprobar({"correo electrónico", "teléfono"} <= malos, "detecta un correo y un teléfono ficticios")
        comprobar(not any(h.columna == "codigo_sie" and h.tipo == "teléfono" for h in privacidad.verificar(base / "privacidad-mala")),
                  "no confunde un código SIE con un teléfono")

        print("liberar")
        ev, _ = liberar.liberar(paq, base / "destino")
        comprobar(ev.aprobada and not (base / "destino").exists(), "con la compuerta aprobada, la simulación no escribe nada")
        lib = yaml.safe_load((paq / "liberacion.yml").read_text(encoding="utf-8"))
        lib["aprobado"] = False
        (paq / "liberacion.yml").write_text(yaml.safe_dump(lib, allow_unicode=True), encoding="utf-8")
        comprobar(not liberar.liberar(paq, base / "destino")[0].aprobada, "se niega si liberacion.yml no está aprobado")
        if shutil.which("git"):
            destino = base / "destino"
            destino.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "main", str(destino)], check=True)
            for k, v in (("user.name", "demo"), ("user.email", "demo@ejemplo.invalid")):
                subprocess.run(["git", "-C", str(destino), "config", k, v], check=True)
            subprocess.run(["git", "-C", str(destino), "commit", "-q", "--allow-empty", "-m", "inicio"], check=True)
            lib["aprobado"] = True
            (paq / "liberacion.yml").write_text(yaml.safe_dump(lib, allow_unicode=True), encoding="utf-8")
            ev, _ = liberar.liberar(paq, destino, ejecutar=True, entrada=lambda _: "no")
            publicado = destino / "paquetes" / paq.name / "liberado" / "agregado.csv"
            comprobar(ev.aprobada and publicado.is_file(), "con --ejecutar crea la rama local con el derivado y no publica sin confirmación")

        print("crear-equipos, congelar y recolectar (simulación)")
        llamadas = []
        gh = equipos.GitHub(lambda args: llamadas.append(args))
        ejemplo = RAIZ / "edicion" / "equipos.ejemplo.csv"
        comprobar(equipos.crear_equipos(ejemplo, "org-ficticia", "dataton-equipo-plantilla", "paquetes-internos", {"D5"},
                                        gh=gh, salida=lambda _: None) == 0 and not llamadas,
                  "crear-equipos simula el plan sin llamar a GitHub")
        repos = [e.repo for e in equipos.leer_equipos(ejemplo)[0]]
        comprobar(equipos.congelar(repos, "org-ficticia", "2099-01-02T18:00:00-04:00", gh=gh, salida=lambda _: None) == 0
                  and not llamadas, "congelar simula el plan sin llamar a GitHub")
        carpeta = base / "entregas"
        shutil.copytree(entrega, carpeta / "d1-eq01-demo")
        inf = recolectar.recolectar([carpeta / "d1-eq01-demo"], escala, base / "informes", salida=lambda _: None)
        comprobar(inf[0]["validar"]["ok"] and (base / "informes" / "resumen.csv").is_file(),
                  "recolectar consolida el informe de una entrega")

        print("init-edicion")
        # Edición ficticia con los mismos códigos de desafío que el repositorio, para que se generen todos sus bloques.
        ficticia = yaml.safe_load((RAIZ / "tests" / "datos" / "edicion-ejemplo.yml").read_text(encoding="utf-8"))
        ids = [d["id"] for d in yaml.safe_load((RAIZ / "edicion" / "edicion.yml").read_text(encoding="utf-8"))["desafios"]]
        ficticia["desafios"] = [{"id": i, "slug": "ficticio", "titulo": "Desafío ficticio",
                                 "responsable_dato": {"codeowner": f"@RESPONSABLE-{i}"}} for i in ids]
        ruta_ficticia = base / "edicion-ficticia.yml"
        ruta_ficticia.write_text(yaml.safe_dump(ficticia, allow_unicode=True, sort_keys=False), encoding="utf-8")
        codigo = cli.main(["init-edicion", "--plantilla", str(RAIZ), "--edicion", str(ruta_ficticia),
                           "--destino", str(base / "edicion-nueva")])
        comprobar(codigo == 0 and (base / "edicion-nueva" / "README.md").is_file(), "crea una edición desde la plantilla")
    return fallas
