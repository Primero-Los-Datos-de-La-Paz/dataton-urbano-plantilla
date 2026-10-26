# Documentación

| Documento | Para quién |
|---|---|
| [arquitectura.md](arquitectura.md) | Organizadores y mantenedores: cómo están organizados los repositorios |
| [compuerta-de-liberacion.md](compuerta-de-liberacion.md) | Responsables del dato y organizadores: cómo se publica un dato interno |
| [nueva-edicion.md](nueva-edicion.md) | Quien quiera organizar su propia edición a partir de esta plantilla |
| [metricas.md](metricas.md) | Jurado, mentores y equipos: cómo se calcula cada medición |
| [windows.md](windows.md) | Quien use Windows: instalación y comandos |
| [github-actions.md](github-actions.md) | Organizadores: validación automática y cuota de minutos |
| [organizadores.md](organizadores.md) | Organizadores: crear equipos, congelar entregas, reunir la evidencia y equipos sin GitHub |

En fases posteriores se agregan: la guía del participante, la guía del responsable del dato, las guías del jurado y de los mentores, las listas de control completas de los organizadores, las preguntas frecuentes, el glosario y la plantilla de lecciones aprendidas.

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
