# Licencias de los datos

## 1. Una licencia por conjunto de datos

Los datos de este repositorio **no tienen una licencia única**. Cada conjunto conserva la licencia o los términos de uso de su fuente original.

- La licencia de cada conjunto se declara en el `datapackage.json` de su paquete (campo `licenses`) y en el catálogo de fuentes (`catalogo/fuentes.csv`, columna `licencia_o_terminos`).
- Si un conjunto no tiene licencia o términos verificados, se marca **SIN VERIFICAR** y no se redistribuye. En su lugar se guarda un script de descarga y la suma SHA-256 esperada del archivo.
- Si una fuente no permite redistribuir, el repositorio guarda solo el enlace, el script de descarga y la suma esperada, nunca el archivo.
- Quien reutilice un conjunto debe respetar la licencia y la atribución que exige su fuente.

## 2. Los datos internos no tienen licencia abierta

Los datos internos de la institución, como los relevamientos que no se han publicado, **no se rigen por una licencia abierta**. Se rigen por las **reglas de uso** de su paquete (`reglas-de-uso.md`), que cada equipo acepta antes de recibirlos. Esas reglas dicen:

- se usan solo para los fines del datatón;
- no se republican;
- no se cruzan para identificar personas;
- se avisa de inmediato si se encuentra un dato personal (ver [SECURITY.md](SECURITY.md)).

Un dato interno solo puede publicarse si pasa la [compuerta de liberación](docs/compuerta-de-liberacion.md). La compuerta exige la decisión del responsable del dato, una revisión de privacidad y una licencia elegida para esa publicación.

## 3. Aportes de los equipos — DECISIÓN PENDIENTE

Los equipos producen datos depurados, diccionarios, fichas y scripts. **La licencia de esos aportes no está decidida.** La decide la dirección jurídica de la institución organizadora (ver [GOVERNANCE.md](GOVERNANCE.md)).

Opciones propuestas para la decisión (no elegidas):

| Tipo de aporte | Opciones |
|---|---|
| Datos derivados y documentación | CC BY 4.0 (exige atribución) · CC0 1.0 (dominio público) · ODbL 1.0 (bases de datos; obliga a compartir igual) |
| Scripts y código | La misma licencia que se elija para el código del repositorio (ver [LICENSE](LICENSE)) |

Limitaciones que debe tener en cuenta la decisión:

- Un dato derivado no puede tener una licencia más abierta que la que permite su fuente.
- La mención de autoría de los equipos está prevista en la convocatoria de cada edición; la licencia debe ser compatible con esa mención.
