# Paquetes de datos

Cada desafío recibe un **paquete de datos**: una carpeta con los datos de partida y todo lo necesario para entenderlos.

Las carpetas se nombran `<ID>-<slug>`, con el código y el nombre corto del desafío definidos en `edicion/edicion.yml` (por ejemplo `D1-base-digital`).

Para crear un paquete nuevo, copia [`_plantilla-paquete/`](_plantilla-paquete/) y renombra la copia.

## Qué tiene un paquete

| Archivo o carpeta | Contenido |
|---|---|
| `README.md` | Ficha de datos: qué es, para qué sirve, qué se espera del equipo |
| `datapackage.json` | Metadatos legibles por máquina (formato Frictionless Data Package) |
| `data/raw/` | Datos originales, **sin editar**, con su suma SHA-256 en `checksums.sha256` |
| `data/interim/` | Conversiones solo mecánicas del original (por ejemplo, de hoja de cálculo a CSV), sin cambiar valores |
| `diccionario.csv` | Una fila por columna: nombre literal, tipo y descripción |
| `procedencia.md` | De dónde vienen los datos, fecha, responsable y periodicidad |
| `reglas-de-uso.md` | Qué se puede y qué no se puede hacer con los datos |
| `problemas-observados.md` | Problemas vistos al preparar el paquete, **sin corregir**: corregirlos es el desafío |
| `linea-base/` | Medición "antes" (scorecard) y nivel de la escala 0–7 |
| `liberacion.yml` | Compuerta de liberación: solo en paquetes con datos internos |

## Reglas

- El dato original no se edita. No se limpia, corrige, imputa ni rellena nada en el paquete: eso lo hacen los equipos.
- Ningún paquete de un repositorio público contiene datos internos ni datos personales.
- Si una fuente no permite redistribuir, el paquete guarda un script de descarga y la suma esperada, no el archivo.
