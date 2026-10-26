# Cómo aportar

Gracias por querer mejorar este repositorio. No necesitas saber programar.

## Formas de aportar

| Quiero… | Qué hago |
|---|---|
| Preguntar algo sobre un paquete de datos | Abre una incidencia con el formulario **Pregunta sobre un paquete** |
| Avisar de un error en un dato | Abre una incidencia con el formulario **Error en un dato**. Describe el problema; no pegues datos personales |
| Proponer una mejora a un conjunto de datos | Entrega la mejora en el repositorio de tu equipo. El responsable del dato la valida con el formulario **Solicitud de validación** |
| Pedir que un dato interno se publique | Formulario **Solicitud de liberación de datos** (lo usa la organización o el responsable del dato) |
| Corregir la documentación o las herramientas | Abre una solicitud de cambios (*pull request*) con la plantilla del repositorio |

## Reglas para cualquier aporte

1. **Nunca subas datos personales.** Eso incluye nombres de personas, cédulas, teléfonos, correos y fechas de nacimiento. Si encuentras uno, sigue [SECURITY.md](SECURITY.md).
2. **El dato original no se edita.** Los archivos de `data/raw/` quedan como llegaron, con su suma SHA-256. Los cambios van en otra carpeta y con un procedimiento que alguien más pueda repetir.
3. **No inventes.** No completes brechas con estimaciones sin evidencia. Si algo no se pudo verificar, escríbelo como "SIN VERIFICAR".
4. **Usa formatos abiertos:** CSV UTF-8, GeoJSON o GeoPackage, JSON, YAML y Markdown.
5. **Las fechas y los pesos se cambian solo en `edicion/edicion.yml`.** Luego se ejecuta `python -m dataton regenerar`.

## Solicitudes de cambios (pull requests)

- Una solicitud por tema.
- Explica qué cambia y por qué.
- Si cambias herramientas en `src/`, agrega o actualiza las pruebas en `tests/` y ejecuta `pytest`.
- Las personas responsables de cada carpeta están en [`.github/CODEOWNERS`](.github/CODEOWNERS) y revisan los cambios de su área.

## Contacto

<!-- dataton:contacto -->
- Buzón institucional: _(por definir en `edicion/edicion.yml`)_
- Incidencias de este repositorio (pestaña *Issues*), con el formulario que corresponda.
<!-- /dataton -->
