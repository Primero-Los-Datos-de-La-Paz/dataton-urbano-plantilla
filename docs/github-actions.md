# Validación automática con GitHub Actions

El archivo [`.github/workflows/validar.yml`](../.github/workflows/validar.yml) se ejecuta cada vez que se suben cambios a `main` o se abre una solicitud de cambios. Hace cuatro cosas:

1. Instala las herramientas.
2. Comprueba que los textos generados estén al día con `edicion/edicion.yml`.
3. Valida todos los paquetes de `paquetes/` (`python -m dataton validar --todos`).
4. Revisa la privacidad de todo el repositorio (`python -m dataton verificar-privacidad .`).

Si algo falla, GitHub marca el commit con una cruz roja y muestra el detalle en la pestaña *Actions*.

## Cuota de minutos

En los **repositorios privados** de una organización con plan gratuito, cada ejecución consume minutos de una **cuota mensual** de GitHub Actions. En los repositorios públicos no hay ese consumo. La cuota exacta depende del plan vigente: consúltala en la configuración de facturación de la organización.

Por eso:

- el flujo es corto: no ejecuta `scorecard`, `nivel` ni `reproducir`;
- en los repositorios de equipo, la evaluación completa (`reproducir`, `scorecard`, `nivel`) **no** se ejecuta en cada cambio. La organización la ejecuta **de forma central al cierre**, en una máquina propia, sobre todas las entregas a la vez.
- Si la cuota se agota, el flujo se puede desactivar desde *Actions → validar → Disable workflow*, sin borrar el archivo.

## Pruebas de las herramientas

El flujo no ejecuta `pytest` para ahorrar minutos. Antes de publicar una versión de la plantilla, ejecuta en local:

```bash
pip install -r requirements-dev.txt
pytest
python -m dataton demo
```
