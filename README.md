# <!-- dataton:valor edicion.nombre -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->

<!-- dataton:valor edicion.descripcion -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->

> **¿Es la plantilla o una edición?** Si en el título dice "por definir", estás viendo la **plantilla**. Para organizar tu propia edición, sigue [docs/nueva-edicion.md](docs/nueva-edicion.md).

## Qué es

Un **datatón urbano de preparación de datos**. Equipos con perfiles distintos trabajan durante unos días sobre datos reales de la ciudad para dejarlos más **confiables, comprensibles, trazables y reutilizables**.

No se busca el proyecto más sofisticado, sino el mejor **activo de datos**: un conjunto de datos con su documentación, su procedencia y un procedimiento que otra persona pueda repetir.

## Qué se hace y qué no

| Sí se hace | No es necesario |
|---|---|
| Encontrar qué datos existen y quién responde por ellos | Construir aplicaciones |
| Depurar, normalizar y validar conjuntos de datos | Tableros o visualizaciones sofisticadas |
| Documentarlos: diccionario, procedencia, periodicidad y responsable | Modelos predictivos o de inteligencia artificial |
| Relacionarlos con el territorio | Calcular indicadores oficiales sin validar |
| Mapear qué datos necesita cada indicador | Estimar valores para llenar vacíos sin evidencia |
| Dejar un procedimiento reproducible | Presentaciones sin un activo de datos reutilizable |

## Empieza en 10 minutos

1. Lee la tabla de **desafíos** (abajo) y elige uno con tu equipo.
2. Abre el paquete de datos de tu desafío en [`paquetes/`](paquetes/). Lee su `README.md`, su `problemas-observados.md` y la medición "antes" de `linea-base/`.
3. Sigue la [guía del participante](docs/guia-participante.md). Tiene dos rutas: con programación y sin programar.
4. Entrega en el repositorio de tu equipo. Lo crea la organización.

## Calendario

<!-- dataton:calendario -->
| Fecha | Actividad |
|---|---|
| (por definir en edicion/edicion.yml) | Inicio de inscripciones. |
| (por definir en edicion/edicion.yml) | Apertura, presentación de desafíos y formación de equipos. |
| (por definir en edicion/edicion.yml) | Trabajo de equipos y preparación de datos. |
| (por definir en edicion/edicion.yml) | Clínica de datos con mentores. |
| (por definir en edicion/edicion.yml) | Cierre de entregas de los equipos. |
| (por definir en edicion/edicion.yml) | Presentación de resultados. |
| (por definir en edicion/edicion.yml) | Validación de las mejoras por los responsables de los datos. |
| (por definir en edicion/edicion.yml) | Informe de aprendizaje de la edición. |
<!-- /dataton -->

Sede: <!-- dataton:valor sede.nombre -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->

## Desafíos

<!-- dataton:desafios -->
| Desafío | Título | Alcance en esta edición | Nivel esperado |
|---|---|---|---|
| D1 | _(por definir en `edicion/edicion.yml`)_ | _(por definir en `edicion/edicion.yml`)_ | _(por definir en `edicion/edicion.yml`)_ |
<!-- /dataton -->

El nivel se mide con la [escala de preparación de 0 a 7](evaluacion/escala-preparacion-0-7.yml), antes y después del trabajo de cada equipo.

## Cómo se valora

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

La [rúbrica](edicion/rubrica.yml) explica qué se revisa en cada criterio y cómo se califica, de 0 a 4. Las herramientas automáticas reúnen evidencia; la nota la pone el jurado.

## Mapa del repositorio

| Carpeta o archivo | Para qué sirve |
|---|---|
| [`edicion/`](edicion/) | `edicion.yml`: el único lugar donde se escriben fechas, pesos, desafíos y responsables. También la rúbrica |
| [`catalogo/`](catalogo/) | Catálogo de fuentes de datos e indicadores |
| [`paquetes/`](paquetes/) | Un paquete de datos por desafío, con ficha, diccionario, procedencia, reglas de uso y medición "antes" |
| [`evaluacion/`](evaluacion/) | Escala de preparación, hoja del jurado, acta de validación y declaración de conflictos |
| [`docs/`](docs/) | Guías para participantes, responsables del dato, jurado, mentores y organizadores |
| [`src/dataton/`](src/dataton/) | Herramientas: `python -m dataton <comando>` |
| [`tests/`](tests/) | Pruebas automáticas de las herramientas, con datos ficticios |
| [`prompts/`](prompts/) | Cómo se construyó el repositorio con ayuda de un asistente |
| [`LICENSE`](LICENSE) y [`LICENSE-DATOS.md`](LICENSE-DATOS.md) | Licencias del código y de los datos |
| [`CONTRIBUTING.md`](CONTRIBUTING.md), [`GOVERNANCE.md`](GOVERNANCE.md), [`SECURITY.md`](SECURITY.md), [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Cómo aportar, quién decide qué, qué hacer ante un dato personal y código de conducta |
| [`CITATION.cff`](CITATION.cff) | Cómo citar este repositorio |

## Instalar las herramientas (opcional)

Se necesita Python 3.11 o más reciente. En Windows, sigue [docs/windows.md](docs/windows.md).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
python -m dataton demo        # debe terminar con OK
```

Qué mide cada comando: [docs/metricas.md](docs/metricas.md). Dudas frecuentes: [docs/preguntas-frecuentes.md](docs/preguntas-frecuentes.md).

## Contacto

<!-- dataton:contacto -->
- Buzón institucional: _(por definir en `edicion/edicion.yml`)_
- Incidencias de este repositorio (pestaña *Issues*), con el formulario que corresponda.
<!-- /dataton -->
