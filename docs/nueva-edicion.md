# Crear una edición nueva

> Versión inicial. Se completará con más detalle en una fase posterior.

1. Copia este repositorio (o usa el botón *Use this template* de GitHub, cuando la plantilla esté publicada).
2. Instala las herramientas (ver la sección "Instalar las herramientas" del README).
3. Copia `edicion/edicion.yml` a un archivo nuevo, fuera de la plantilla, y complétalo con los datos de tu edición. Toma las fechas y los pesos solo de tu convocatoria oficial.
4. Desde la carpeta de la plantilla, ejecuta:

   ```bash
   python -m dataton init-edicion --edicion RUTA/A/TU/edicion.yml --destino ../nombre-de-tu-edicion
   ```

5. Revisa la lista de "campos por definir" que muestra el comando.
6. Cada vez que cambies `edicion/edicion.yml` en tu edición, ejecuta `python -m dataton regenerar`.
7. Antes de publicar, ejecuta `python -m dataton regenerar --comprobar` para confirmar que todo está al día.
