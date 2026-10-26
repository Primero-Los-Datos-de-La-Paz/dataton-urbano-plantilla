# Carpeta `edicion/`

Aquí vive [`edicion.yml`](edicion.yml), el archivo que describe **una** edición del datatón.

## Regla principal

Las fechas, los pesos de la rúbrica, la sede, los desafíos, los responsables, el contacto y las reglas de visibilidad se escriben **solo** en `edicion.yml`. Los demás archivos los copian de aquí con:

```bash
python -m dataton regenerar
```

Para saber si algún archivo quedó desactualizado, sin cambiar nada:

```bash
python -m dataton regenerar --comprobar
```

## Qué hay en `edicion.yml`

| Sección | Contenido |
|---|---|
| `edicion` | Nombre, programa, número, año, ciudad, institución, organizadores, roles y documentos de origen |
| `github` | Organización de GitHub y nombres de los repositorios |
| `sede` | Lugar de las actividades presenciales |
| `calendario` | Actividades con fecha de inicio y de fin (`AAAA-MM-DD`). Si solo se sabe el mes, se usa `mes: AAAA-MM` |
| `desafios` | Código, título, alcance, nivel esperado y unidad responsable del dato de cada desafío |
| `rubrica` | Criterios de valoración y sus pesos (deben sumar 100) |
| `contacto` | Buzón institucional. Nunca teléfonos ni correos personales |
| `visibilidad` | Visibilidad de cada repositorio y reglas para los datos internos |

Un valor `null` significa "por definir". Las herramientas lo aceptan, pero lo listan como pendiente.

## Cómo se marcan los textos generados

En los archivos Markdown, el texto que sale de `edicion.yml` está entre marcas invisibles:

```text
<!-- dataton:… -->
(aquí va el texto generado)
<!-- /dataton -->
```

(En el ejemplo se usa "…" en lugar del nombre real del bloque para que la herramienta no lo reemplace.)

Si editas a mano el texto que está entre esas marcas, `regenerar` lo sobrescribirá. Edita `edicion.yml`.

En los archivos YAML y en `CODEOWNERS`, las marcas son comentarios de línea: `# dataton:nombre` y `# /dataton`.

`CITATION.cff` se genera completo.
