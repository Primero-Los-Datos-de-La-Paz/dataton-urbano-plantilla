# Seguridad y datos personales

## Si subiste o encontraste un dato personal

Un dato personal es, por ejemplo, el nombre de una persona, su cédula, teléfono, correo, dirección particular o fecha de nacimiento.

**Avisa de inmediato.** Escribe al buzón institucional (abajo):

- indica el **archivo, la columna y la fila**;
- **no copies el dato** en el mensaje;
- **no abras una incidencia pública.**

**Borrar el archivo no alcanza.** Git guarda el historial: el dato sigue en los commits anteriores, y en las copias o bifurcaciones que alguien haya hecho.

**Qué hace la organización:**

1. Si el repositorio es público, lo pasa a **privado** de inmediato.
2. **Quita el dato del historial**: lo reescribe con una herramienta como `git filter-repo`, o **recrea el repositorio** sin el dato y archiva el anterior.
3. Pide a GitHub que borre las vistas en caché, si el repositorio fue público.
4. Pide a <!-- dataton:valor areas.juridica -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton --> y a <!-- dataton:valor areas.tecnologia -->_(por definir en `edicion/edicion.yml`)_<!-- /dataton --> que **evalúen el incidente**: qué se expuso, durante cuánto tiempo y a quién hay que avisar.
5. Avisa al responsable del dato.
6. Registra el incidente y lo que se cambió para que no se repita (ver [lecciones-aprendidas.md](docs/lecciones-aprendidas.md)).

Mientras tanto, nadie descarga, copia ni reenvía el archivo afectado.

## Si encontraste una credencial o un token

No lo uses. Avisa por el buzón con el nombre del archivo. La organización revoca la credencial y limpia el historial.

## Prevención

- `python -m dataton verificar-privacidad .` revisa columnas y patrones antes de publicar.
- La validación automática de cada repositorio (pestaña *Actions*) hace la misma revisión en cada cambio.
- Ningún dato interno sale del repositorio privado si no pasa la [compuerta de liberación](docs/compuerta-de-liberacion.md).

## Contacto

<!-- dataton:contacto -->
- Buzón institucional: _(por definir en `edicion/edicion.yml`)_
- Incidencias de este repositorio (pestaña *Issues*), con el formulario que corresponda.
<!-- /dataton -->

Para temas de seguridad o privacidad, usa solo el buzón, nunca una incidencia.
