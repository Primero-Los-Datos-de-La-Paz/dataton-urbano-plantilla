# Glosario

| Término | Qué significa |
|---|---|
| **Activo de datos** | Un conjunto de datos junto con su documentación, su procedencia y su procedimiento. Es lo que se entrega y se valora |
| **Agregado** | Dato resumido por grupos (por ejemplo, total de estudiantes por escuela), sin registros de personas |
| **Brecha** | Lo que falta para que un dato o un indicador sea verificable |
| **Checksum o suma SHA-256** | Un código que identifica el contenido exacto de un archivo. Si el archivo cambia, el código cambia. Se usa para comprobar que un archivo no se alteró |
| **Clave** | Columna o columnas que identifican cada fila sin repetirse (por ejemplo, un código de escuela) |
| **Compuerta de liberación** | Los requisitos que debe cumplir un dato interno antes de publicar un derivado de él. Ver [compuerta-de-liberacion.md](compuerta-de-liberacion.md) |
| **Commit** | Cada vez que guardas cambios en un repositorio de GitHub |
| **Completitud** | Proporción de celdas que tienen valor |
| **Consistencia** | Que los datos no se contradigan (por ejemplo, que el total sea igual a la suma de sus partes) |
| **CSV UTF-8** | Archivo de texto con columnas separadas por comas, con una codificación que conserva tildes y eñes |
| **Datapackage** (`datapackage.json`) | Archivo con los metadatos de un paquete de datos, legible por máquinas (estándar Frictionless) |
| **Dato interno** | Dato de una institución que no está publicado. No tiene licencia abierta y se rige por reglas de uso |
| **Dato personal** | Información que identifica a una persona: nombre, cédula, teléfono, correo, dirección particular o fecha de nacimiento |
| **Derivado** | Un conjunto nuevo producido a partir de otro, por ejemplo agregándolo o anonimizándolo |
| **Diccionario de datos** | Tabla que explica cada columna: nombre, tipo, descripción, unidad y valores posibles |
| **Dominio** | La lista de valores válidos de una columna |
| **Escala de preparación (0 a 7)** | Niveles que van de "desconocido" a "listo para Ciudad Inteligente". Ver [la escala](../evaluacion/escala-preparacion-0-7.yml) |
| **Etiqueta `entrega-final`** | Marca que la organización pone en el último commit de cada equipo al cierre |
| **GeoJSON / GeoPackage** | Formatos abiertos para datos con ubicación (puntos, líneas, polígonos) |
| **Incidencia (*issue*)** | Un mensaje con formulario en un repositorio de GitHub, para preguntas, errores o solicitudes |
| **Interim** (`data/interim/`) | Carpeta con conversiones solo mecánicas del original, por ejemplo de hoja de cálculo a CSV |
| **Licencia** | Lo que se permite hacer con un dato o con un código |
| **Línea base** | La medición "antes" del trabajo de los equipos |
| **Paquete de datos** | Carpeta con los datos de un desafío y todo lo necesario para entenderlos |
| **Procedencia** | De dónde viene un dato, cuándo se obtuvo y qué cambios tuvo |
| **Raw** (`data/raw/`) | Carpeta con el dato original, que no se edita nunca |
| **Repositorio** | Carpeta en GitHub con archivos y su historial de cambios |
| **Reproducible** | Que otra persona pueda repetir el procedimiento y obtener el mismo resultado |
| **Responsable del dato** | La unidad que produce o custodia el dato y que acepta o rechaza las mejoras |
| **Rúbrica** | Los criterios de valoración, con su peso y la escala de notas de 0 a 4 |
| **Scorecard** | La medición de las dimensiones de calidad con `python -m dataton scorecard` |
| **Territorialidad** | Que un registro se pueda ubicar en el territorio (coordenadas o claves territoriales) |
| **Unicidad** | Que no haya filas duplicadas según su clave |
| **Validez** | Que los valores cumplan su formato y su dominio |
