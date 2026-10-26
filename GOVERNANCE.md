# Gobernanza

Quién decide qué en el datatón. Los nombres de las unidades salen de `edicion/edicion.yml`.

## Principios

- **Cada responsable del dato decide sobre sus datos.** La organización del datatón no valida ni modifica datos de otras áreas.
- **Toda mejora se acepta o se rechaza con un motivo escrito** antes de incorporarse al catálogo institucional.
- **Las fichas de indicadores no son cifras oficiales.** Antes de cualquier uso oficial las revisa: <!-- dataton:valor areas.estadistica -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->.
- **Las reglas de uso, las licencias y la privacidad** las revisan <!-- dataton:valor areas.juridica -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton --> y <!-- dataton:valor areas.tecnologia -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->.
- **Ejecución del datatón:** <!-- dataton:valor areas.organizacion -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->. **Aprueba:** <!-- dataton:valor areas.aprobacion -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->.

## Matriz de responsabilidades (RACI)

R = hace el trabajo; A = responde por el resultado (una sola unidad); C = se le consulta; I = se le informa.

<!-- dataton:raci -->
| Actividad | R (hace) | A (responde) | C (consultado) | I (informado) |
|---|---|---|---|---|
| _(por definir en `edicion/edicion.yml`)_ | | | | |
<!-- /dataton -->

> La asignación formal debe validarse internamente en la institución.

## Roles en esta edición

<!-- dataton:roles -->
| Rol | Quién |
|---|---|
| _(por definir en `edicion/edicion.yml`)_ | |
<!-- /dataton -->

## Responsables del dato por desafío

<!-- dataton:responsables -->
| Desafío | Responsable del dato | Marcador en CODEOWNERS |
|---|---|---|
| D1 _(por definir en `edicion/edicion.yml`)_ | _(por definir en `edicion/edicion.yml`)_ | `@RESPONSABLE-D1` |
<!-- /dataton -->

Los marcadores `@RESPONSABLE-…` de [`.github/CODEOWNERS`](.github/CODEOWNERS) se reemplazan por cuentas o equipos reales de GitHub solo cuando la institución designa formalmente a las personas.

## Visibilidad de los repositorios

<!-- dataton:visibilidad -->
Todo repositorio nace privado. Solo pasa a público con aprobación explícita, repositorio por repositorio.

| Repositorio | Visibilidad inicial | Visibilidad prevista | Condición |
|---|---|---|---|
| `dataton-urbano-plantilla` | privado | público | Aprobación explícita tras la revisión de calidad y privacidad. |
| `dataton-equipo-plantilla` | privado | público | Aprobación explícita tras la revisión de calidad y privacidad. |
| _(por definir en `edicion/edicion.yml`)_ | privado | público | Aprobación explícita; sin datos internos ni datos personales. |
| _(por definir en `edicion/edicion.yml`)_ | privado | privado | Nunca se hace público. |

- Los datos internos en su forma original solo se guardan en el repositorio de paquetes internos.
- Un dato interno solo sale de allí mediante la compuerta de liberación (docs/compuerta-de-liberacion.md).
<!-- /dataton -->

## Cómo se decide

| Decisión | Quién propone | Quién decide | Dónde queda registrada |
|---|---|---|---|
| Aceptar o rechazar una mejora | Equipo participante | Responsable del dato | Incidencia **Solicitud de validación** y [acta de validación](evaluacion/acta-validacion.md) |
| Publicar un derivado de un dato interno | Organización o responsable del dato | Responsable del dato, con la revisión jurídica y de tecnología | Incidencia **Solicitud de liberación de datos** y `liberacion.yml` del paquete |
| Cambiar la visibilidad de un repositorio | Organización | Unidad que aprueba la edición | Registro de la edición |
| Elegir licencias | Organización | Área jurídica | `LICENSE` y `LICENSE-DATOS.md` |
| Cambiar fechas, pesos o responsables | Organización | Unidad que aprueba la edición | `edicion/edicion.yml` (historial de Git) |
| Valorar las entregas | Jurado | Jurado | [Hoja del jurado](evaluacion/hoja-jurado.md) |
