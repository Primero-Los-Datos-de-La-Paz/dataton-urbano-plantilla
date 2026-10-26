# Guía del responsable del dato

Eres la unidad que produce o custodia un conjunto de datos del datatón. **Tú decides sobre tus datos**: la organización no los valida ni los modifica por ti.

## Antes del datatón: qué entregas

| Qué | Para qué |
|---|---|
| El conjunto de datos, o el acceso a él | Es la materia prima del paquete |
| Una persona de contacto de tu unidad (punto focal) | Responde consultas de los equipos, por escrito |
| Lo que sepas del dato: qué contiene, cómo se recoge, cada cuánto se actualiza, quién lo usa | Completa la procedencia y el diccionario |
| Las restricciones: ¿hay datos personales?, ¿se puede publicar algo? | Define las reglas de uso y la compuerta de liberación |

La organización arma el paquete:

- guarda el **original sin cambios**, con su suma SHA-256;
- hace solo conversiones mecánicas de formato;
- documenta los problemas que ve, **sin corregirlos**;
- mide el nivel "antes".

Si hay datos internos, el paquete vive en un repositorio privado y solo lo ven los equipos que aceptaron las reglas.

## Durante el datatón

- Responde las consultas de los equipos, de preferencia por escrito: incidencia **Pregunta sobre un paquete** o buzón institucional.
- Si un equipo encuentra un dato personal, te avisarán sin copiar el valor.

## Después: validar o rechazar cada mejora

Cada equipo pide la validación de sus mejoras con la incidencia **Solicitud de validación**.

**Plazo de validación:** <!-- dataton:fecha validacion -->(por definir en edicion/edicion.yml)<!-- /dataton -->.

Para cada solicitud:

1. **Revisa la evidencia:**
   - el informe automático del equipo (`evaluacion/informes/`);
   - su `antes-despues.md`;
   - el procedimiento, que se puede repetir con `python -m dataton reproducir`.
2. **Decide:**
   - **aceptada:** la mejora es correcta y útil para tu unidad;
   - **rechazada:** no lo es, o no se puede verificar.
3. **Escribe el motivo, siempre**, también cuando la aceptas. Por ejemplo:
   - "Aceptada: las coordenadas coinciden con nuestro registro de campo."
   - "Rechazada: unifica dos categorías que en nuestro formulario son distintas."
4. **Registra la decisión:**
   - en la incidencia: campos "Decisión del responsable del dato" y "Motivo de la decisión";
   - y en el [acta de validación](../evaluacion/acta-validacion.md): conjunto, mejora, evidencia, decisión, motivo, unidad, fecha y referencia.

Sin una decisión registrada, la mejora **no se incorpora** al catálogo institucional.

## Indicadores

Las fichas de indicadores no son cifras oficiales. Antes de cualquier uso oficial las revisa: <!-- dataton:valor areas.estadistica -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->.

## Publicar un derivado de un dato interno

Si decides que se puede publicar una versión agregada o anonimizada, se usa la [compuerta de liberación](compuerta-de-liberacion.md). Necesitas:

- tu **decisión por escrito**: fecha y referencia de la nota, el acta o el correo institucional;
- la revisión de <!-- dataton:valor areas.juridica -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton --> y de <!-- dataton:valor areas.tecnologia -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->;
- una licencia para lo que se publica.

El original nunca se publica.
