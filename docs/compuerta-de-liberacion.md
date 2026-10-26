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
| Archivos del derivado que se publican, solo en formato abierto | `archivos_publicables` |
| Aprobación final | `aprobado: true` |

## Reglas

1. Si falta un solo campo, la liberación no ocurre.
2. La liberación publica una **copia nueva y limpia**, sin el historial del repositorio privado.
3. El archivo original nunca se publica si alguna vez contuvo datos personales.
4. La liberación crea una solicitud de cambios en el repositorio público. Una persona la revisa y la fusiona; nunca se fusiona de forma automática.
5. Lo publicado conserva la referencia a su `liberacion.yml` para la trazabilidad.

## Cómo se usa la herramienta

```bash
# Simulación (por defecto): muestra qué se publicaría, sin escribir nada.
python -m dataton liberar RUTA/DEL/PAQUETE --destino RUTA/DEL/CLON/PUBLICO

# Prepara la rama local con el derivado y muestra los comandos para subirla y abrir la solicitud.
# Solo los ejecuta si escribes "si". Nunca fusiona.
python -m dataton liberar RUTA/DEL/PAQUETE --destino RUTA/DEL/CLON/PUBLICO --ejecutar
```

La herramienta se niega si falta cualquier campo, si `aprobado` no es `true`, si un archivo publicable no está en formato abierto o si `verificar-privacidad` encuentra algo grave.
