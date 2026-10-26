"""Pruebas de validar, scorecard, nivel, reproducir, verificar-privacidad, liberar y demo.

Usan solo los datos sintéticos de tests/datos/demo, copiados a una carpeta temporal.
"""

import shutil
import zipfile
from pathlib import Path

import pytest
import yaml

from dataton import cli, demo, liberar, nivel, privacidad, reproducir, scorecard, validar

RAIZ = Path(__file__).resolve().parents[1]
DEMO = Path(__file__).resolve().parent / "datos" / "demo"
ESCALA = RAIZ / "evaluacion" / "escala-preparacion-0-7.yml"


@pytest.fixture
def base(tmp_path):
    destino = tmp_path / "demo"
    shutil.copytree(DEMO, destino)
    return destino


# --- validar --------------------------------------------------------------------

def test_validar_paquete_y_entrega(base):
    assert validar.validar(base / "paquete-demo").ok
    assert validar.validar(base / "entrega-demo").ok


def test_validar_detecta_suma_distinta_y_archivo_faltante(base):
    paq = base / "paquete-demo"
    (paq / "data" / "raw" / "escuelas.csv").write_text("x\n", encoding="utf-8")
    (paq / "reglas-de-uso.md").unlink()
    res = validar.validar(paq)
    assert not res.ok
    assert any("suma" in e for e in res.errores)
    assert any("reglas-de-uso.md" in e for e in res.errores)


def test_validar_entrega_incompleta(base):
    (base / "entrega-demo" / "autoria.yml").unlink()
    assert not validar.validar(base / "entrega-demo").ok


def test_cli_validar_devuelve_codigo(base):
    assert cli.main(["validar", str(base / "paquete-demo")]) == 0


# --- scorecard ------------------------------------------------------------------

def test_scorecard_mide_con_reglas(base):
    sc = scorecard.scorecard(base / "paquete-demo")
    r = sc["recursos"]["data/interim/escuelas.csv"]
    assert r["completitud"]["valor"] == 1.0
    assert r["consistencia"]["valor"] == 1.0
    assert r["territorialidad"]["aproximada"] is True
    assert sc["paquete_dimensiones"]["documentacion"]["valor"] == 1.0
    assert "exactitud" in sc["revision_humana"]


def test_scorecard_sin_reglas_no_inventa(base):
    paq = base / "paquete-demo"
    (paq / "reglas-calidad.yml").unlink()
    r = scorecard.scorecard(paq)["recursos"]["data/interim/escuelas.csv"]
    assert r["validez"]["medible"] is False
    assert r["consistencia"]["medible"] is False
    assert r["territorialidad"]["medible"] is False


def test_scorecard_detecta_inconsistencia(base):
    paq = base / "paquete-demo"
    ruta = paq / "data" / "interim" / "escuelas.csv"
    ruta.write_text(ruta.read_text(encoding="utf-8").replace(",120,20,100,", ",999,20,100,"), encoding="utf-8")
    r = scorecard.scorecard(paq)["recursos"]["data/interim/escuelas.csv"]
    assert r["consistencia"]["valor"] < 1.0


@pytest.mark.parametrize("texto,esperado", [
    ("16°30'10.85\"S 68°07'20.94\"W", (-16.5030, -68.1225)),
    ("16°29'32.21\"S 68° 8'21.89\"W", (-16.4923, -68.1394)),
    ("-16.331662, -67.957466", (-16.3317, -67.9575)),
])
def test_leer_coordenada(texto, esperado):
    lat, lon = scorecard.leer_coordenada(texto)
    assert (round(lat, 4), round(lon, 4)) == esperado


def test_coordenada_ilegible():
    assert scorecard.leer_coordenada("texto cualquiera") is None


# --- nivel ----------------------------------------------------------------------

def test_nivel_propone_5_en_el_demo(base):
    assert nivel.evaluar(base / "paquete-demo", ESCALA)["nivel_propuesto"] == 5


def test_nivel_baja_si_falta_documentacion(base):
    paq = base / "paquete-demo"
    texto = (paq / "procedencia.md").read_text(encoding="utf-8").replace("| Periodicidad | Anual |", "| Periodicidad | Desconocida |")
    (paq / "procedencia.md").write_text(texto, encoding="utf-8")
    r = nivel.evaluar(paq, ESCALA)
    assert r["nivel_propuesto"] == 1
    faltan = [c["id"] for n in r["niveles"] for c in n["faltantes"]]
    assert "periodicidad_conocida" in faltan


def test_nivel_nunca_propone_6_o_7(base):
    r = nivel.evaluar(base / "paquete-demo", ESCALA)
    assert all(n["revision_humana"] for n in r["niveles"] if n["nivel"] >= 6)


# --- reproducir -----------------------------------------------------------------

def test_reproducir_sin_ejecutar_solo_planifica(base):
    res = reproducir.reproducir(base / "entrega-demo")
    assert not res.ejecutado and not res.errores


def test_reproducir_ejecuta_en_copia_y_compara(base):
    entrega = base / "entrega-demo"
    antes = (entrega / "entrega" / "salida" / "resultado.csv").read_bytes()
    assert reproducir.reproducir(entrega, ejecutar=True).ok
    assert (entrega / "entrega" / "salida" / "resultado.csv").read_bytes() == antes


def test_reproducir_detecta_diferencia(base):
    script = base / "entrega-demo" / "entrega" / "scripts" / "01_sumar.py"
    script.write_text(script.read_text(encoding="utf-8").replace('int(f["a"]) + int(f["b"])', '0'), encoding="utf-8")
    res = reproducir.reproducir(base / "entrega-demo", ejecutar=True)
    assert res.ejecutado and res.difieren == ["resultado.csv"]


# --- verificar-privacidad ---------------------------------------------------------

def test_privacidad_detecta_sin_mostrar_valores(base, capsys):
    hallazgos = privacidad.verificar(base / "privacidad-mala")
    tipos = {h.tipo for h in hallazgos if h.gravedad == "alta"}
    assert {"correo electrónico", "teléfono"} <= tipos
    assert cli.main(["verificar-privacidad", str(base / "privacidad-mala")]) == 1
    salida = capsys.readouterr().out
    assert "ejemplo.invalid" not in salida and "71234567" not in salida


def test_privacidad_no_confunde_codigos_sie(base):
    hallazgos = privacidad.verificar(base / "privacidad-mala")
    assert not [h for h in hallazgos if h.columna == "codigo_sie"]


def test_privacidad_respeta_archivo_de_exclusiones(base):
    (base / ".dataton-privacidad-ignorar").write_text("privacidad-mala\n", encoding="utf-8")
    assert not [h for h in privacidad.verificar(base) if h.gravedad == "alta"]


def test_privacidad_detecta_metadatos_de_autor_en_xlsx(tmp_path):
    ruta = tmp_path / "libro.xlsx"
    with zipfile.ZipFile(ruta, "w") as z:
        z.writestr("docProps/core.xml", "<cp:coreProperties><dc:creator>Persona Ficticia</dc:creator></cp:coreProperties>")
        z.writestr("xl/workbook.xml", '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                   'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
                   '<sheet name="H" r:id="rId1"/></sheets></workbook>')
        z.writestr("xl/_rels/workbook.xml.rels", '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   '<Relationship Id="rId1" Target="worksheets/sheet1.xml"/></Relationships>')
        z.writestr("xl/worksheets/sheet1.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
                   '<sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>col</t></is></c></row></sheetData></worksheet>')
    tipos = {h.tipo for h in privacidad.verificar(ruta)}
    assert "metadatos de autor" in tipos


# --- liberar --------------------------------------------------------------------

def _cambiar_liberacion(paq, **cambios):
    lib = yaml.safe_load((paq / "liberacion.yml").read_text(encoding="utf-8"))
    lib.update(cambios)
    (paq / "liberacion.yml").write_text(yaml.safe_dump(lib, allow_unicode=True), encoding="utf-8")


def test_liberar_simulacion_no_escribe(base):
    ev, mensajes = liberar.liberar(base / "paquete-demo", base / "destino")
    assert ev.aprobada and not (base / "destino").exists()
    assert any("simulación" in m for m in mensajes)


def test_liberar_se_niega_sin_aprobacion(base):
    _cambiar_liberacion(base / "paquete-demo", aprobado=False)
    assert cli.main(["liberar", str(base / "paquete-demo"), "--destino", str(base / "destino")]) == 1


def test_liberar_se_niega_con_formato_propietario(base):
    paq = base / "paquete-demo"
    (paq / "derivado" / "agregado.xlsx").write_bytes(b"PK")
    _cambiar_liberacion(paq, archivos_publicables=["derivado/agregado.xlsx"])
    ev = liberar.evaluar(paq)
    assert not ev.aprobada and any("formato abierto" in f for f in ev.faltantes)


def test_liberar_se_niega_si_hay_datos_personales(base):
    paq = base / "paquete-demo"
    shutil.copyfile(base / "privacidad-mala" / "contactos.csv", paq / "derivado" / "contactos.csv")
    _cambiar_liberacion(paq, archivos_publicables=["derivado/contactos.csv"])
    assert liberar.evaluar(paq).hallazgos


# --- demo -----------------------------------------------------------------------

def test_demo_termina_en_ok(capsys):
    assert demo.ejecutar() == []
