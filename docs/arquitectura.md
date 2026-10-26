# Arquitectura de los repositorios

> Este documento describe la estructura que existe hoy. Se escribió a partir de las instrucciones de construcción (carpeta `prompts/` de cada edición), porque el documento de arquitectura original no estaba disponible al construir la plantilla.

## Repositorios

| Repositorio | Contenido | Visibilidad |
|---|---|---|
| `dataton-urbano-plantilla` | Esta plantilla: estructura, herramientas y documentación, sin datos de ninguna ciudad | Nace privado; puede hacerse público con aprobación |
| `dataton-equipo-plantilla` | Plantilla del repositorio de entrega de cada equipo | Nace privado; puede hacerse público con aprobación |
| Repositorio de la edición | Copia de la plantilla con su `edicion/edicion.yml`, catálogo y paquetes de datos públicos | Nace privado; puede hacerse público con aprobación |
| Repositorio de paquetes internos | Paquetes con datos internos en su forma original | Siempre privado |
| Repositorios de equipo | Uno por equipo, creado desde la plantilla de equipo | Privados |

Los nombres exactos de cada edición están en `edicion/edicion.yml`, sección `github`.

## Un solo lugar para los datos de la edición

`edicion/edicion.yml` guarda el nombre de la edición, las fechas, la sede, los desafíos, los pesos de la rúbrica, los responsables por desafío, el contacto institucional y las reglas de visibilidad. Ningún otro archivo los escribe a mano. Los textos que los muestran están marcados y se generan con `python -m dataton regenerar` (ver `edicion/README.md`).

## Cómo se crea una edición

```text
dataton-urbano-plantilla  +  edicion.yml de la nueva edición
              │
              ▼   python -m dataton init-edicion --edicion … --destino …
repositorio de la edición (copia de la plantilla con los textos generados)
```

## Carpetas

| Carpeta | Contenido |
|---|---|
| `edicion/` | `edicion.yml` y su explicación |
| `catalogo/` | Fuentes e indicadores |
| `paquetes/` | Un paquete por desafío; `_plantilla-paquete/` es el modelo |
| `src/dataton/` | Herramientas (`python -m dataton <comando>`) |
| `tests/` | Pruebas con datos sintéticos |
| `evaluacion/` | Escala de preparación, rúbrica y documentos del jurado |
| `docs/` | Guías |
| `prompts/` | Instrucciones de construcción con un asistente |
| `.github/` | Formularios de incidencia, plantilla de solicitud de cambios y `CODEOWNERS` |

## Flujo de los datos dentro de un paquete

```text
data/raw/      original, inmutable, con suma SHA-256
   │  solo cambios mecánicos (conversión de formato)
   ▼
data/interim/  mismo contenido en formato abierto
   │  trabajo de los equipos, con procedimiento reproducible
   ▼
entrega del equipo  →  validación del responsable del dato  →  catálogo institucional
```

Un dato interno sale del repositorio privado solo por la [compuerta de liberación](compuerta-de-liberacion.md).
