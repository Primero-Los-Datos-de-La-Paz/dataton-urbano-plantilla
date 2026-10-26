# Organizar una edición propia en una hora

Esta plantilla sirve para cualquier ciudad o institución. Todo lo propio de una edición se escribe en un solo archivo: `edicion/edicion.yml`.

## Lo que necesitas

- Tu **convocatoria oficial**, con las fechas, los desafíos y los criterios de valoración con sus pesos.
- Python 3.11 o más reciente, y las herramientas instaladas (ver el [README](../README.md#instalar-las-herramientas-opcional)).
- Una organización de GitHub, si vas a usar repositorios de equipo.

## Paso a paso

| Tiempo | Paso |
|---|---|
| 10 min | **1. Copia la plantilla.** En GitHub, usa *Use this template* (cuando la plantilla esté publicada), o clona o descarga el repositorio |
| 25 min | **2. Completa tu `edicion.yml`.** Copia `edicion/edicion.yml` a un archivo fuera de la plantilla, por ejemplo `mi-edicion.yml`, y llena cada sección con datos **tomados de tu convocatoria**. Si algo no está en la convocatoria, déjalo en `null`: la herramienta lo listará como pendiente. No inventes fechas ni pesos |
| 5 min | **3. Genera tu edición:** `python -m dataton init-edicion --edicion mi-edicion.yml --destino ../mi-edicion` |
| 5 min | **4. Revisa los pendientes.** El comando lista los campos por definir. Complétalos en `../mi-edicion/edicion/edicion.yml` y ejecuta `python -m dataton regenerar` dentro de esa carpeta |
| 5 min | **5. Ajusta la rúbrica**, si tu convocatoria usa otros criterios: `edicion/rubrica.yml` debe tener los mismos `id` que `edicion.yml`. Los pesos van solo en `edicion.yml` y deben sumar 100 |
| 5 min | **6. Comprueba:** `python -m dataton regenerar --comprobar`, `python -m dataton validar --todos` y `python -m dataton demo` |
| 5 min | **7. Revisa los textos** generados en el README y en las guías, por si quieres ajustar la redacción fuera de las marcas `<!-- dataton:… -->` |

Después, prepara los paquetes de datos de cada desafío con el modelo `paquetes/_plantilla-paquete/` (eso lleva más de una hora: depende de tus datos).

## Qué no cambiar

- No escribas fechas, pesos ni nombres de unidades fuera de `edicion.yml`. Si un texto los necesita, usa una marca de las que ya existen en los documentos (`<!-- dataton:fecha …`, `<!-- dataton:valor …`, `<!-- dataton:desafio …`).
- No guardes datos internos en el repositorio de la edición: usa un repositorio privado de paquetes internos.

## Reutilizar los prompts

La carpeta [`prompts/`](../prompts/) explica cómo se construyó una edición con ayuda de un asistente de programación, en fases con revisión humana (P0 a P7).

Para reutilizarlos:

1. Copia los prompts de una edición anterior a tu espacio de trabajo, **no** al repositorio público de tu edición.
2. Reemplaza lo propio de esa ciudad (nombres de unidades, desafíos, archivos internos) por lo de la tuya.
3. Escribe un archivo de instrucciones generales con tus reglas: privacidad, visibilidad de los repositorios, convocatoria que manda.
4. Ejecuta una fase a la vez y revisa el resultado antes de pasar a la siguiente.

La plantilla no trae los prompts de ninguna edición porque contienen datos de esa ciudad.
