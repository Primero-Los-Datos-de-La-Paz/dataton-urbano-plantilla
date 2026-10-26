# Preguntas frecuentes

## Sobre el datatón

**¿Tengo que saber programar?**
No. Hay una ruta sin programación: hoja de cálculo, OpenRefine, QGIS o pasos documentados. Ver la [guía del participante](guia-participante.md).

**¿Hay que construir una aplicación o un tablero?**
No. Se valora el activo de datos: datos depurados, documentados y con un procedimiento que se pueda repetir.

**¿Hay premio en dinero?**
Lo dice la convocatoria de cada edición. En esta: <!-- dataton:valor edicion.reconocimiento -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->

**¿Cuándo cierran las entregas?**
<!-- dataton:fecha cierre_entregas limite -->(por definir en edicion/edicion.yml)<!-- /dataton -->. Cuenta lo que esté en la rama `main` de tu repositorio a esa hora.

**¿Cómo se valora?**
Con siete criterios y sus pesos (ver el [README](../README.md#cómo-se-valora)). El jurado pone una nota de 0 a 4 por criterio, con la [rúbrica](../edicion/rubrica.yml).

## Sobre los datos

**Encontré un error en los datos. ¿Lo corrijo en el original?**
No. El original no se toca. Corrige en una copia, documenta el cambio y deja el procedimiento. Si no tienes evidencia para corregirlo, documéntalo como problema.

**Encontré un nombre, un teléfono o una cédula. ¿Qué hago?**
No lo copies en ningún lado. Avisa de inmediato por el buzón institucional, indicando archivo, columna y fila. Ver [SECURITY.md](../SECURITY.md).

**¿Puedo usar los datos internos para otro proyecto?**
No. Solo para los fines del datatón y según sus reglas de uso.

**Faltan datos. ¿Puedo estimarlos?**
No sin evidencia. Escribe la brecha: qué falta, dónde podría estar y quién podría tenerlo.

**¿Mi cálculo de un indicador es oficial?**
No. Las fichas documentan fuente, periodo, numerador, denominador y brecha. Antes de cualquier uso oficial las revisa: <!-- dataton:valor areas.estadistica -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->.

**¿En qué formato entrego?**
En formatos abiertos: CSV UTF-8, GeoJSON o GeoPackage, JSON, YAML y Markdown. No entregues XLSX como resultado.

## Sobre GitHub

**No tengo cuenta de GitHub.**
Puedes crear una gratis, o entregar un ZIP a la organización (ver la [guía del participante](guia-participante.md#7-si-no-usas-github)).

**¿Cómo subo archivos sin Git?**
En tu repositorio: *Add file → Upload files*, arrastra los archivos y pulsa *Commit changes*.

**Apareció una cruz roja en *Actions*.**
La revisión automática encontró algo: falta un archivo o hay un posible dato personal. Abre el detalle para ver qué es. Si no lo entiendes, abre una incidencia.

**Subí un archivo por error. ¿Lo borro?**
Si es un dato personal o interno, **borrarlo no alcanza**, porque Git guarda el historial. Avisa a la organización. Si es otro error, puedes borrarlo o reemplazarlo.

**¿Quién ve mi repositorio?**
Tu equipo y la organización. Es privado. Al cierre se congela y se archiva.

## Sobre las mediciones

**¿La herramienta decide mi nota?**
No. Mide lo que se puede medir de forma objetiva (completitud, validez, unicidad, consistencia…) y propone un nivel. La nota la pone el jurado. Ver [metricas.md](metricas.md).

**¿Por qué mi nivel propuesto es bajo si mejoré mucho?**
Revisa la lista de criterios "faltantes" que muestra `python -m dataton nivel`. A menudo falta la documentación: descripciones del diccionario, periodicidad o responsable.
