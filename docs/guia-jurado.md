# Guía del jurado

Tu tarea es valorar **activos de datos**, no aplicaciones ni presentaciones. No gana necesariamente el trabajo con más tecnología ni el más vistoso, sino el activo más confiable, comprensible, trazable y reutilizable.

## Antes de evaluar

1. Firma la [declaración de conflictos de interés](../evaluacion/declaracion-conflictos.md). Si tienes relación con un equipo, no evalúas su entrega.
2. Lee la [rúbrica](../edicion/rubrica.yml): qué respalda cada criterio y qué significa cada nota de 0 a 4.
3. Lee qué mide cada herramienta en [metricas.md](metricas.md).

## Criterios y pesos

<!-- dataton:rubrica -->
| Criterio | Peso |
|---|---:|
| Calidad y consistencia del activo de datos | _(por definir en `edicion/edicion.yml`)_ |
| Documentación y trazabilidad | _(por definir en `edicion/edicion.yml`)_ |
| Reproducibilidad | _(por definir en `edicion/edicion.yml`)_ |
| Cobertura del desafío / KPI | _(por definir en `edicion/edicion.yml`)_ |
| Territorialización e interoperabilidad | _(por definir en `edicion/edicion.yml`)_ |
| Gobernanza y uso responsable | _(por definir en `edicion/edicion.yml`)_ |
| Utilidad para decisiones y reutilización | _(por definir en `edicion/edicion.yml`)_ |
<!-- /dataton -->

## Cómo evaluar una entrega

1. **Abre el informe automático** del equipo en `evaluacion/informes/<entrega>.md`. Es **evidencia**, no una nota: estructura, privacidad, mediciones y nivel propuesto.
2. **Revisa la entrega** en su repositorio, en la etiqueta `entrega-final`:
   - `entrega/ficha-por-desafio.md`: ¿responde a la pregunta del desafío?
   - `entrega/antes-despues.md`: ¿la mejora es real y está medida con las mismas reglas?
   - `entrega/diccionario.csv` y `entrega/procedencia.md`: ¿un tercero los entiende?
   - el procedimiento: ¿se puede repetir? Si son scripts, la organización puede ejecutar `reproducir`. Si son pasos manuales, comprueba que se pueden seguir.
3. **Califica** cada criterio de 0 a 4 en la [hoja del jurado](../evaluacion/hoja-jurado.md). El puntaje de cada criterio es peso × nota ÷ 4, y el total va de 0 a 100.
4. **Explica tu nota** con la evidencia que revisaste.

## Señales de alerta

| Señal | Qué hacer |
|---|---|
| Un posible dato personal | Avisa a la organización por el buzón, sin copiar el valor. Afecta el criterio de gobernanza |
| Valores inventados o vacíos rellenados sin evidencia | Baja la nota de calidad; anótalo |
| Cálculos presentados como cifras oficiales | Anótalo: las fichas no son cifras oficiales |
| Mejora sin medición antes/después | La calidad y la cobertura no se pueden comprobar |
| El procedimiento no se puede repetir | Afecta la reproducibilidad |

## Qué no hacer

- No premies la complejidad técnica por sí misma.
- No uses el nivel propuesto ni las mediciones automáticas como nota: son evidencia.
- No compartas datos internos de las entregas fuera de la evaluación.
