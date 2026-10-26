# Métricas: cómo se calcula cada medición

Las herramientas **reúnen evidencia; no deciden el puntaje.** El puntaje lo pone el jurado con la rúbrica. Si algo no se puede medir de forma objetiva, la herramienta no lo mide: lo informa como "no medible" o lo deja para revisión humana.

Todo se calcula con reglas deterministas: con los mismos archivos y las mismas reglas, el resultado es siempre el mismo.

## Reglas de medición de cada paquete: `reglas-calidad.yml`

Cada paquete puede declarar sus reglas en un archivo `reglas-calidad.yml`. Las reglas **describen cómo medir, no corrigen nada**. Ejemplo (el modelo está en `paquetes/_plantilla-paquete/reglas-calidad.yml`):

```yaml
recursos:
  data/interim/tabla.csv:
    campos_minimos: [codigo, nombre]        # vacío = todas las columnas
    clave: [codigo]                         # columnas que identifican una fila
    validez:
      - {columna: codigo, patron: "^\\d{8}$"}
      - {columna: total, tipo: entero, minimo: 0}
      - {columna: estado, dominio: [Bueno, Regular, Malo]}
    consistencia:
      - {regla: menor_o_igual, a: funcionando, b: total}
      - {regla: suma, total: total, partes: [inicial, primaria, secundaria]}
    territorio:
      coordenadas: coordenadas              # o bien  lat: columna  y  lon: columna
      recuadro: {lat_min: -10, lat_max: -9, lon_min: -60, lon_max: -59}
      fuente_recuadro: "De dónde sale el recuadro"
vinculos:                                   # opcional: relaciones con otras tablas
  - {desde: "data/interim/a.csv:codigo", hacia: "data/interim/b.csv:codigo"}
```

Las columnas se indican por nombre exacto, por nombre sin espacios a los lados o por letra (A, B, … AA).

## Dimensiones que se miden (`python -m dataton scorecard`)

Cada medición se informa con su numerador, su denominador y su valor (de 0 a 1). Una celda está **vacía** si no tiene nada o solo tiene espacios.

| Dimensión | Cálculo | Si no hay reglas |
|---|---|---|
| **Completitud** | Celdas no vacías en los campos mínimos ÷ (filas × campos mínimos) | Se usan todas las columnas |
| **Validez** | Celdas no vacías que cumplen su regla ÷ celdas no vacías revisadas. Las reglas posibles son `tipo` (entero, número, fecha AAAA-MM-DD), `patron` (expresión regular completa), `dominio` (lista cerrada de valores) y `minimo`/`maximo`. Las celdas vacías no cuentan aquí: ya cuentan en completitud | **No medible** |
| **Unicidad** | Filas con clave completa y única ÷ filas con clave completa. También informa cuántas filas no tienen clave y cuántas claves se repiten | Se cuentan filas idénticas (y se avisa que no hay clave declarada) |
| **Consistencia** | Filas que cumplen la regla ÷ filas evaluables. `menor_o_igual`: a ≤ b, evaluable si ambos son números. `suma`: total = suma de las partes; las partes vacías cuentan como 0 (si no se declara lo contrario con `vacio_como_cero: false`); evaluable si el total es un número | **No medible** |
| **Territorialidad** | Filas con coordenada legible **dentro del recuadro** ÷ total de filas. Una coordenada es legible si es decimal ("lat, lon") o está en grados, minutos y segundos con hemisferio (`16°30'10"S 68°07'20"W`). **Es una verificación aproximada**: usa un rectángulo, no el polígono del municipio | **No medible** |
| **Documentación** | Columnas con descripción no vacía en `diccionario.csv` ÷ columnas de la tabla | — |
| **Trazabilidad** (paquete) | Componentes presentes ÷ 3: `procedencia.md` con contenido; `checksums.sha256`; registro de cambios (una sección cuyo título contenga "cambios" en `procedencia.md`, o un archivo `registro-cambios.md`) | — |
| **Accesibilidad** (paquete) | Promedio de dos partes: (recursos locales en formato abierto ÷ recursos locales) y (1 si `datapackage.json` declara licencias o reglas de uso, 0 si no). Formatos abiertos: CSV, JSON, GeoJSON, GeoPackage, GeoTIFF, TXT, Markdown, YAML, Parquet. XLSX no lo es | — |

Por defecto se miden las tablas CSV y GeoJSON de `data/`. Si `reglas-calidad.yml` lista recursos, se miden solo esos.

## Dimensiones que NO se miden de forma automática

| Dimensión | Por qué |
|---|---|
| **Exactitud** | Requiere comparar con la realidad o con una fuente de referencia. La valoran el jurado o el responsable del dato |
| **Oportunidad** | Depende de la fecha del fenómeno y del uso previsto. La valoran el jurado o el responsable del dato |

El comando `scorecard` lo dice de forma explícita en su resultado (sección `revision_humana`).

## Nivel de preparación (`python -m dataton nivel`)

El comando **propone** el nivel más alto cuyos criterios se cumplen todos, junto con los de todos los niveles anteriores. Los criterios y umbrales están en [`evaluacion/escala-preparacion-0-7.yml`](../evaluacion/escala-preparacion-0-7.yml) y se pueden ajustar allí sin tocar el código.

| Nivel | Criterios verificables |
|---|---|
| 1 Identificado | `datapackage.json` tiene al menos un recurso, o `procedencia.md` declara la fuente |
| 2 Documentado | Documentación ≥ umbral; `procedencia.md` declara periodicidad y responsable del dato en filas `\| Periodicidad \| … \|` y `\| Responsable del dato \| … \|`, sin "desconocida", "por confirmar", "sin verificar" ni "por definir" |
| 3 Depurado | En cada tabla: completitud ≥ umbral, validez ≥ umbral (con reglas), clave declarada sin duplicados y consistencia ≥ umbral (con reglas) |
| 4 Conectable | En cada tabla, territorialidad ≥ umbral, o un vínculo declarado en `reglas-calidad.yml` |
| 5 Reutilizable | Accesibilidad = 100 % y existe `reglas-de-uso.md` |
| 6 Accionable y 7 Listo para Ciudad Inteligente | **Revisión humana**: el comando nunca los propone |

Umbrales iniciales (para revisar con el jurado y la UIIEM): documentación 80 %, completitud 90 %, validez 95 %, consistencia 95 %, territorialidad 80 %.

## Reproducibilidad (`python -m dataton reproducir`)

- **Entrega de equipo:** se ejecutan `entrega/scripts/*.py` en orden alfabético, en una **copia temporal**, con `entrega/` como carpeta de trabajo. Luego se compara cada archivo listado en `entrega/salida/checksums.sha256` con su suma SHA-256.
- **Paquete:** se ejecutan `scripts/*.py` y se comparan los archivos de `data/interim/` listados en `checksums.sha256`.
- **Reglas de ejecución:**
  - antes de ejecutar se borran las salidas declaradas de la copia, para comprobar que los scripts las vuelven a producir;
  - cada script tiene un límite de 600 segundos;
  - sin `--ejecutar` solo se muestra el plan.
- **Otros procedimientos** (cuadernos, OpenRefine, QGIS, pasos manuales) se listan para revisión humana.

## Privacidad (`python -m dataton verificar-privacidad`)

- **Nombres de columna:** busca nombre, apellido, teléfono, celular, correo, cédula, CI, docente, director y fecha de nacimiento. Son de gravedad **alta** las de apellido, teléfono, correo, cédula, CI y nacimiento; el resto es **revisar** (por ejemplo, "nombre" suele ser el nombre de una institución).
- **Valores:** busca correos, teléfonos (8 dígitos que empiezan con 6 o 7), cédulas con sigla de expedición y fechas en columnas de nacimiento. Todos son de gravedad alta.
- **Falsos positivos:**
  - las columnas de código (por su nombre: código, SIE, id…) no se revisan con los patrones de teléfono ni de cédula;
  - un número de 8 dígitos cuenta como teléfono solo si la columna se llama como un contacto, o si es una columna de texto y el número va junto a una palabra de contacto (cel, telf, teléfono, WhatsApp…).
- **Xlsx:** también avisa si los metadatos de autor están llenos.
- **Qué informa:** archivo, columna, tipo de patrón y cantidad. **Nunca el valor.**
- **Código de salida:** termina con error si hay hallazgos de gravedad alta.
- **Exclusiones:** `.dataton-privacidad-ignorar` excluye rutas de las revisiones de carpeta completa. Es solo para datos de prueba con datos personales ficticios a propósito.

## Liberación (`python -m dataton liberar`)

Ver [compuerta-de-liberacion.md](compuerta-de-liberacion.md). El comando se niega si falta cualquier campo de `liberacion.yml`, si `aprobado` no es `true`, si algún archivo publicable no está en formato abierto o si `verificar-privacidad` encuentra algo grave en esos archivos.
