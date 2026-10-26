# Guía de mentores

La clínica de datos es: <!-- dataton:fecha clinica -->(por definir en edicion/edicion.yml)<!-- /dataton -->. Después de la clínica, las consultas se atienden por escrito.

Tu papel es **orientar, no resolver**. Ayuda a los equipos a ver los problemas y a decidir cómo tratarlos, pero no hagas el trabajo por ellos ni des por buenas correcciones sin evidencia.

## 1. Calidad

Preguntas que ayudan:

- ¿Qué columnas son la **clave** de la tabla? ¿Hay duplicados o claves vacías?
- ¿Qué valores son válidos en cada columna? ¿Hay errores de tipeo o variantes de la misma categoría?
- ¿Hay reglas entre columnas? Por ejemplo, "funcionando ≤ total" o "total = suma de las partes".
- ¿Un vacío significa "cero", "no aplica" o "no respondió"?

Recuerda:

- Corregir sin evidencia **empeora** el dato. Es mejor documentar el problema que inventar una solución.
- El "después" se mide con **las mismas reglas** que el "antes" (`reglas-calidad.yml`).

## 2. Documentación

- Cada columna del resultado necesita una descripción, una unidad y, si corresponde, un dominio (`diccionario.csv`).
- La procedencia debe decir de dónde viene cada archivo, qué se cambió y con qué procedimiento.
- Prueba de fuego: ¿alguien que no estuvo en el equipo entiende los datos con solo leer la documentación?

## 3. Información geográfica

- Las coordenadas deben estar en **dos columnas decimales** (latitud y longitud), con el datum declarado (por ejemplo, WGS 84 / EPSG:4326).
- En el hemisferio sur la latitud es negativa, y en el hemisferio occidental la longitud también.
- Ojo con las coordenadas repetidas: pueden ser varias unidades en un mismo edificio, o un error de copia.
- Para unir con el territorio (distrito, zona), documenta la fuente de los límites y su fecha.
- La medición de territorialidad de las herramientas es **aproximada**: usa un recuadro, no el polígono exacto.

## 4. Privacidad

- **Nada de datos personales** en las entregas: nombres de personas, cédulas, teléfonos, correos ni fechas de nacimiento.
- Si un equipo encuentra uno, **no lo copia**: avisa por el buzón institucional con el archivo, la columna y la fila.
- Los datos internos no se republican, ni siquiera como extractos o capturas de pantalla.
- Una mejora con datos personales no se puede validar ni publicar.
- La herramienta `python -m dataton verificar-privacidad` ayuda, pero no reemplaza la revisión humana.

## Cuándo derivar

| Duda | A quién |
|---|---|
| Qué significa un dato o cómo se recoge | Al responsable del dato, por escrito |
| Privacidad o reglas de uso | A la organización, por el buzón institucional |
| Herramientas o repositorio | A la organización, con una incidencia |
