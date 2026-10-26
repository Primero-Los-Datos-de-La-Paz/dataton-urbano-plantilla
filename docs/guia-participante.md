# Guía del participante

Esta guía te lleva de principio a fin. **No necesitas saber programar.** Si algo no se entiende, pregunta en la clínica de datos o abre una incidencia **Pregunta sobre un paquete**.

## Fechas clave

| Momento | Fecha |
|---|---|
| Apertura y formación de equipos | <!-- dataton:fecha apertura -->(por definir en edicion/edicion.yml)<!-- /dataton --> |
| Clínica de datos con mentores | <!-- dataton:fecha clinica -->(por definir en edicion/edicion.yml)<!-- /dataton --> |
| **Cierre de entregas** | <!-- dataton:fecha cierre_entregas limite -->(por definir en edicion/edicion.yml)<!-- /dataton --> |
| Presentación de resultados | <!-- dataton:fecha presentacion -->(por definir en edicion/edicion.yml)<!-- /dataton --> |

El calendario completo está en el [README](../README.md#calendario).

## 1. Antes de empezar

1. **Elige un desafío** con tu equipo (tabla de desafíos del [README](../README.md#desafíos)).
2. **Recibe tu repositorio.** La organización crea un repositorio privado para tu equipo, llamado `d{N}-eq{NN}-{nombre}`, y te invita por correo. **Acepta la invitación** de GitHub.
   - Si no tienes cuenta de GitHub, ve al [paso 7](#7-si-no-usas-github).
3. **Lee y acepta las reglas.** En tu repositorio, pestaña *Issues*, abre **Acuerdo de reglas de uso**, marca las casillas con tu equipo y ciérrala.

## 2. Conoce tu paquete de datos

En la carpeta [`paquetes/`](../paquetes/) de este repositorio está el paquete de tu desafío. Lee, en este orden:

1. `README.md`: qué es, para qué sirve y **qué se espera de tu equipo**.
2. `problemas-observados.md`: los problemas que ya se vieron. **No están corregidos**: ese es tu trabajo.
3. `linea-base/`: la medición **antes**. Al final medirás el **después** con las mismas reglas.
4. `diccionario.csv`, `procedencia.md` y `reglas-de-uso.md`.

Si tu desafío usa datos internos, la organización te da acceso a ellos después de que aceptes las reglas.

## 3. Elige tu ruta de trabajo

### Ruta A: sin programar

Usa las herramientas que ya conoces:

| Herramienta | Para qué | Qué guardas como procedimiento |
|---|---|---|
| Hoja de cálculo (LibreOffice Calc, Excel, Google Sheets) | Revisar, filtrar y corregir en una copia | Cada paso en `entrega/pasos-manuales.md` |
| OpenRefine | Unificar categorías, quitar espacios, separar columnas | El historial de operaciones (Undo/Redo → Extract → JSON) en `entrega/scripts/` |
| QGIS | Revisar coordenadas y unir con límites territoriales | El modelo o el proyecto en `entrega/scripts/`, y los pasos en `pasos-manuales.md` |

Reglas de la ruta A:

- Trabaja siempre en **una copia**. El original no se toca.
- Anota **cada paso**, de modo que otra persona pueda repetirlo y llegar al mismo resultado.
- Guarda el resultado en **CSV UTF-8** (en la hoja de cálculo: "Guardar como" → CSV, codificación UTF-8). No entregues `.xlsx` como resultado.

### Ruta B: con programación

- Escribe tus scripts (Python, R…) en `entrega/scripts/`. Si son varios, numéralos en el orden en que se ejecutan: `01_leer.py`, `02_depurar.py`…
- Los scripts se ejecutan desde la carpeta `entrega/`: leen de `datos/` y escriben en `salida/`.
- No uses rutas de tu computadora, como `C:\Users\…`.
- Comprueba que tu procedimiento se puede repetir:

  ```bash
  python -m dataton reproducir . --ejecutar
  ```

Las dos rutas valen lo mismo. Se valora que el procedimiento se pueda repetir, no la herramienta.

## 4. Arma tu entrega

Tu repositorio ya tiene la estructura. Completa:

| Archivo o carpeta | Qué va |
|---|---|
| `autoria.yml` | Integrantes y si aceptan que su nombre aparezca en el reconocimiento |
| `entrega/ficha-equipo.yml` | Desafío, fichas o indicadores, conjuntos y nivel antes/después |
| `entrega/datos/` | Datos de partida, o un enlace con su suma, si no se pueden copiar |
| `entrega/scripts/` o `entrega/pasos-manuales.md` | El procedimiento |
| `entrega/salida/` | El resultado, en formato abierto |
| `entrega/diccionario.csv` | Una fila por columna del resultado, con su descripción |
| `entrega/procedencia.md` | De dónde viene cada dato y qué cambiaste |
| `entrega/ficha-por-desafio.md` | Lo que pide tu desafío |
| `entrega/antes-despues.md` | La medición antes y después |

Al terminar, guarda las sumas del resultado y valida:

```bash
python -m dataton sumas entrega/salida
python -m dataton validar .
```

Si no puedes ejecutar comandos, pide ayuda a la organización.

## 5. Sube archivos sin usar Git

1. En GitHub, entra en tu repositorio y en la carpeta correcta, por ejemplo `entrega/salida`.
2. Pulsa **Add file → Upload files**.
3. Arrastra los archivos.
4. Escribe qué subes en "Commit changes" y pulsa **Commit changes**.

Para editar un archivo de texto, ábrelo y pulsa el lápiz ✎. Al terminar, pulsa **Commit changes**.

Después de cada subida, la pestaña **Actions** revisa la estructura y busca datos personales. Si aparece una cruz roja, abre el detalle para ver qué falta.

## 6. Mide el antes y el después

La **escala de preparación** va de 0 a 7:

| Nivel | Nombre | En pocas palabras |
|---:|---|---|
| 0 | Desconocido | No se sabe si el dato existe |
| 1 | Identificado | Se sabe dónde está |
| 2 | Documentado | Tiene definición, periodicidad y responsable |
| 3 | Depurado | Cumple criterios mínimos de calidad |
| 4 | Conectable | Se puede unir con otros datos por un código o por el territorio |
| 5 | Reutilizable | Cualquier persona autorizada lo puede usar |
| 6 | Accionable | Responde una pregunta o apoya una decisión concreta |
| 7 | Listo para Ciudad Inteligente | Puede alimentar servicios y sistemas de forma controlada |

**Ejemplo ficticio** de un registro de escuelas:

| | Antes | Después |
|---|---|---|
| Situación | Las coordenadas están en un solo campo y en tres formatos; el diccionario está vacío; no se sabe quién actualiza los datos | Coordenadas en dos columnas decimales; diccionario completo; responsable y periodicidad confirmados; total de estudiantes = suma por nivel |
| Completitud | 82 % | 96 % |
| Consistencia | 90 % | 100 % |
| Documentación | 0 % | 100 % |
| Nivel | 1 · Identificado | 4 · Conectable |

Para medir el "después" con **las mismas reglas** que el "antes":

1. Copia el archivo `reglas-calidad.yml` del paquete de tu desafío (si tiene uno) a `entrega/reglas-calidad.yml`.
2. En ese archivo, cambia cada nombre de archivo del paquete (por ejemplo `data/interim/tabla.csv`) por el de tu resultado (por ejemplo `salida/tabla.csv`). Si cambiaste nombres de columna, cámbialos también. No cambies las reglas.
3. Mide:

   ```bash
   python -m dataton scorecard entrega
   python -m dataton nivel entrega
   ```

Copia los resultados en `entrega/antes-despues.md`. La herramienta **propone** un nivel; el jurado y el responsable del dato lo confirman.

## 7. Si no usas GitHub

1. Pide a la organización la estructura de la entrega: es la misma de la plantilla de equipo.
2. Prepara tu entrega en una carpeta con esa estructura (`entrega/` y `autoria.yml`).
3. Comprímela en un **ZIP** y envíala a la organización por el buzón institucional, antes del cierre de entregas.
4. La organización revisa que no tenga datos personales y la sube por ti.

## 8. Qué NO hacer

- **No subas datos personales:** nombres de personas, cédulas, teléfonos, correos, direcciones particulares ni fechas de nacimiento. Si lo hiciste por error, **avisa de inmediato** ([SECURITY.md](../SECURITY.md)). Borrar el archivo no alcanza: Git guarda el historial.
- **No republiques datos internos** fuera de tu repositorio privado. Ni capturas de pantalla ni extractos.
- **No edites el dato original:** trabaja en una copia y documenta cada cambio.
- **No inventes valores** ni rellenes vacíos sin evidencia. Si algo falta, escríbelo como brecha.
- **No presentes cálculos como cifras oficiales.**

## 9. Cierre y presentación

- **Cierre de entregas:** <!-- dataton:fecha cierre_entregas limite -->(por definir en edicion/edicion.yml)<!-- /dataton -->. Lo que esté en la rama `main` a esa hora es tu entrega.
- **Después del cierre:** la organización congela tu repositorio con la etiqueta `entrega-final` y lo archiva; queda en solo lectura.
- **Presentación:** cuenta qué cambió en los datos, cómo lo mediste y qué falta. Muestra el antes y el después.
- **Validación:** después, el responsable del dato acepta o rechaza cada mejora, con un motivo. Plazo: <!-- dataton:fecha validacion -->(por definir en edicion/edicion.yml)<!-- /dataton -->.
- **Reconocimiento:** <!-- dataton:valor edicion.reconocimiento -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->
