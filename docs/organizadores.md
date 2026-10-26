# Guía para organizadores: equipos, entregas y evaluación

> Versión inicial. Las listas de control completas de antes, durante y después se agregan en una fase posterior.

Todos los comandos se ejecutan desde la carpeta del repositorio de la edición, con las herramientas instaladas (ver el README). **Todo lo que cambia GitHub es una simulación salvo que agregues `--ejecutar`**, y aun así pide escribir `si` antes de hacer cualquier cambio.

## 0. Requisitos

- La cuenta de `gh` debe tener permisos de administración en la organización. Para crear equipos e invitar personas hace falta el alcance `admin:org` (`gh auth refresh -s admin:org`).
- La plantilla de equipo (`dataton-equipo-plantilla`) debe estar en la organización y **marcada como repositorio plantilla**.
- En `edicion/edicion.yml`: la organización, los nombres de los repositorios y `paquete_interno: true` en los desafíos que tienen paquete interno.

## 1. Preparar la lista de equipos

1. Copia `edicion/equipos.ejemplo.csv` a `edicion/equipos.csv`. Git no guarda ese archivo porque contiene usuarios y contactos.
2. Una fila por equipo:

   | Columna | Contenido |
   |---|---|
   | `equipo_id` | Número del equipo (01, 02…) |
   | `nombre` | Nombre del equipo |
   | `desafio` | D1 a D5 |
   | `usuarios_github` | Usuarios separados por `;` |
   | `contacto` | Correo del equipo, solo para la organización |

3. El repositorio de cada equipo se llamará `d{N}-eq{NN}-{nombre-corto}`, por ejemplo `d5-eq02-mapa-abierto`.

## 2. Crear los repositorios y equipos

```bash
python -m dataton crear-equipos --csv edicion/equipos.csv            # simulación: muestra cada comando
python -m dataton crear-equipos --csv edicion/equipos.csv --ejecutar # aplica, después de escribir "si"
```

Para cada equipo, el comando:

1. crea el repositorio **privado** desde la plantilla de equipo;
2. invita a cada usuario a la organización, si todavía no es miembro;
3. crea un equipo de la organización con escritura **solo** en su repositorio;
4. agrega a cada usuario al equipo `participantes-dN`, que da **lectura** al repositorio de paquetes internos si su desafío tiene paquete interno;
5. abre las incidencias "Acuerdo de reglas de uso" y "Checklist de entrega".

Si algo ya existe, lo omite: puedes volver a ejecutarlo sin duplicar nada. Si GitHub niega una acción por permisos, se detiene. Todo queda en `edicion/equipos_creados.csv`.

> **Importante:** GitHub da acceso al repositorio de paquetes internos **completo**, no por carpeta. Hoy solo el desafío D5 tiene paquete interno. Si en otra edición hay varios, conviene un repositorio interno por desafío.

Las personas reciben una invitación por correo y deben **aceptarla** antes de poder entrar.

## 3. Equipos sin cuenta de GitHub

1. La organización crea el repositorio del equipo con `crear-equipos` y deja vacío `usuarios_github`, o crea el repositorio a mano desde la plantilla.
2. El equipo entrega un **ZIP** con la misma estructura de la plantilla de equipo: carpeta `entrega/` y `autoria.yml`.
3. La organización revisa que el ZIP no tenga datos personales (`python -m dataton verificar-privacidad CARPETA`) y lo sube al repositorio con *Add file → Upload files*, indicando en el mensaje del commit que es la entrega del equipo.
4. Para evaluar sin pasar por GitHub, descomprime cada ZIP en una subcarpeta y usa `recolectar --carpeta` (paso 5).

## 4. Congelar las entregas al cierre

```bash
python -m dataton congelar --csv edicion/equipos.csv --fecha-limite 2099-01-31T18:00:00-04:00            # simulación
python -m dataton congelar --csv edicion/equipos.csv --fecha-limite 2099-01-31T18:00:00-04:00 --ejecutar
```

La fecha límite va en formato ISO, **con zona horaria**. Usa la de tu convocatoria; el ejemplo es ficticio. Para cada repositorio, el comando:

1. registra en `evaluacion/entregas.csv` el SHA de `main`, la fecha de ese commit y si quedó dentro del plazo;
2. crea la etiqueta `entrega-final` en ese SHA;
3. archiva el repositorio (queda en solo lectura).

No borra ni cambia commits. Si un commit llegó fuera de plazo, lo marca y lo decide el jurado.

## 5. Reunir la evidencia automática

```bash
python -m dataton recolectar --org NOMBRE-ORG --csv edicion/equipos.csv   # clona en la etiqueta entrega-final
python -m dataton recolectar --carpeta entregas-zip/                      # entregas ya descargadas
```

- **Qué hace:** clona cada repositorio en solo lectura y ejecuta `validar`, `verificar-privacidad`, `scorecard` y `nivel`. Deja en `evaluacion/informes/` un informe `.md` y uno `.json` por equipo, más un `resumen.csv`. Git no guarda esa carpeta.
- **Reproducibilidad:** **no** ejecuta el código de los equipos. Para comprobarla, usa en un entorno aislado:

  ```bash
  python -m dataton reproducir entregas-clonadas/REPO --ejecutar
  ```

- Los informes son **evidencia**. La nota la pone el jurado con `evaluacion/hoja-jurado.md` y `edicion/rubrica.yml`.

## 6. Validación por los responsables del dato

Cada mejora se acepta o se rechaza, con un motivo, en `evaluacion/acta-validacion.md` y en la incidencia **Solicitud de validación**.
