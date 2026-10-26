# <!-- dataton:valor edicion.nombre -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->

Repositorio de un **datatón urbano de preparación de datos**. El objetivo no es construir aplicaciones: es dejar datos más confiables, comprensibles, trazables y reutilizables.

> **¿Es la plantilla o una edición?** Si en el título de arriba dice "por definir", estás viendo la **plantilla**. Para crear tu propia edición, sigue [docs/nueva-edicion.md](docs/nueva-edicion.md).

<!-- dataton:valor edicion.descripcion -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton -->

## Calendario

<!-- dataton:calendario -->
| Fecha | Actividad |
|---|---|
| (por definir en edicion/edicion.yml) | Inicio de inscripciones. |
| (por definir en edicion/edicion.yml) | Apertura, presentación de desafíos y formación de equipos. |
| (por definir en edicion/edicion.yml) | Trabajo de equipos y preparación de datos. |
| (por definir en edicion/edicion.yml) | Clínica de datos con mentores. |
| (por definir en edicion/edicion.yml) | Presentación de resultados. |
| (por definir en edicion/edicion.yml) | Validación de las mejoras por los responsables de los datos. |
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

## Mapa del repositorio

| Carpeta o archivo | Para qué sirve |
|---|---|
| [`edicion/`](edicion/) | `edicion.yml`: el único lugar donde se escriben fechas, pesos, desafíos y responsables |
| [`catalogo/`](catalogo/) | Catálogo de fuentes de datos e indicadores |
| [`paquetes/`](paquetes/) | Un paquete de datos por desafío, con ficha, diccionario, procedencia y reglas de uso |
| [`evaluacion/`](evaluacion/) | Escala de preparación, rúbrica y documentos del jurado |
| [`src/dataton/`](src/dataton/) | Herramientas: `python -m dataton <comando>` |
| [`tests/`](tests/) | Pruebas automáticas de las herramientas |
| [`docs/`](docs/) | Guías para participantes, responsables de datos, jurado, mentores y organizadores |
| [`prompts/`](prompts/) | Instrucciones usadas para construir el repositorio con ayuda de un asistente |
| [`LICENSE`](LICENSE) y [`LICENSE-DATOS.md`](LICENSE-DATOS.md) | Licencias del código y de los datos |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Cómo aportar |
| [`GOVERNANCE.md`](GOVERNANCE.md) | Quién decide qué |
| [`SECURITY.md`](SECURITY.md) | Qué hacer si se sube un dato personal por error |
| [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md) | Código de conducta |
| [`CITATION.cff`](CITATION.cff) | Cómo citar este repositorio |

## Instalar las herramientas

Se necesita Python 3.11 o más reciente.

```bash
python -m venv .venv
# macOS o Linux:
source .venv/bin/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pip install -e .
python -m dataton --help
```

## Contacto

<!-- dataton:contacto -->
- Buzón institucional: _(por definir en `edicion/edicion.yml`)_
- Incidencias de este repositorio (pestaña *Issues*), con el formulario que corresponda.
<!-- /dataton -->
