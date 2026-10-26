# Documentación

| Documento | Para quién |
|---|---|
| [guia-participante.md](guia-participante.md) | Participantes: de principio a fin, con y sin programación |
| [guia-responsable-del-dato.md](guia-responsable-del-dato.md) | Unidades responsables de los datos: qué entregan y cómo validan |
| [guia-jurado.md](guia-jurado.md) | Jurado: cómo valorar una entrega |
| [guia-mentores.md](guia-mentores.md) | Mentores: calidad, documentación, información geográfica y privacidad |
| [organizadores.md](organizadores.md) | Organizadores: listas de control y paso a paso con las herramientas |
| [nueva-edicion.md](nueva-edicion.md) | Quien quiera organizar su propia edición en una hora |
| [preguntas-frecuentes.md](preguntas-frecuentes.md) | Todos |
| [glosario.md](glosario.md) | Todos: los términos explicados |
| [metricas.md](metricas.md) | Jurado, mentores y equipos: cómo se calcula cada medición |
| [compuerta-de-liberacion.md](compuerta-de-liberacion.md) | Responsables del dato y organizadores: cómo se publica un derivado de un dato interno |
| [arquitectura.md](arquitectura.md) | Mantenedores: cómo están organizados los repositorios |
| [windows.md](windows.md) | Quien use Windows: instalación y comandos |
| [github-actions.md](github-actions.md) | Organizadores: validación automática y cuota de minutos |
| [lecciones-aprendidas.md](lecciones-aprendidas.md) | Organizadores: plantilla del informe de aprendizaje |

## Comandos

| Comando | Qué hace |
|---|---|
| `python -m dataton init-edicion` | Crea una edición desde la plantilla |
| `python -m dataton regenerar` | Actualiza los textos generados desde `edicion.yml` |
| `python -m dataton validar` | Valida un paquete o una entrega |
| `python -m dataton scorecard` | Mide las dimensiones de calidad |
| `python -m dataton nivel` | Propone el nivel 0–7 |
| `python -m dataton reproducir` | Ejecuta el procedimiento y compara las sumas |
| `python -m dataton verificar-privacidad` | Busca posibles datos personales |
| `python -m dataton liberar` | Publica un derivado si pasa la compuerta |
| `python -m dataton sumas` | Escribe `checksums.sha256` de una carpeta |
| `python -m dataton crear-equipos` | Crea los repositorios y equipos de GitHub (simulación por defecto) |
| `python -m dataton congelar` | Etiqueta y archiva las entregas (simulación por defecto) |
| `python -m dataton recolectar` | Reúne las entregas y escribe los informes automáticos |
| `python -m dataton demo` | Prueba todo con datos sintéticos |
