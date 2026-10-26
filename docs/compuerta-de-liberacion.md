# Compuerta de liberación

La compuerta de liberación es el único camino por el que un dato interno, o un derivado de él, puede salir del repositorio privado de paquetes internos hacia un repositorio público.

## Qué se necesita

Todo debe estar en el archivo `liberacion.yml` del paquete (modelo en `paquetes/_plantilla-paquete/liberacion.yml`) y en una incidencia **Solicitud de liberación de datos**.

| Requisito | Campo en `liberacion.yml` |
|---|---|
| Clasificación del conjunto original | `clasificacion` |
| Qué se libera: derivado agregado, derivado anonimizado u original | `que_se_libera` |
| Nivel mínimo de agregación y columnas incluidas y excluidas | `agregacion_minima` |
| Decisión del responsable del dato, con unidad, fecha y referencia del acta | `decision_responsable` |
| Revisión de privacidad: herramienta sin hallazgos, metadatos de autor eliminados, exclusiones registradas, revisiones jurídica y de tecnología | `revision_privacidad` |
| Licencia de lo que se publica | `licencia` |
| Script reproducible que genera el derivado desde el original | `script_derivado` |
| Aprobación final | `aprobado: true` |

## Reglas

1. Si falta un solo campo, la liberación no ocurre.
2. La liberación publica una **copia nueva y limpia**, sin el historial del repositorio privado.
3. El archivo original nunca se publica si alguna vez contuvo datos personales.
4. La liberación crea una solicitud de cambios en el repositorio público. Una persona la revisa y la fusiona; nunca se fusiona de forma automática.
5. Lo publicado conserva la referencia a su `liberacion.yml` para la trazabilidad.

La herramienta que aplica estas reglas (`python -m dataton liberar`) se agrega en una fase posterior.
