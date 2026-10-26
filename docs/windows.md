# Instalar y usar las herramientas en Windows

## 1. Instalar Python

1. Descarga Python 3.12 (o más reciente, desde la 3.11) del sitio oficial, python.org.
2. Al instalar, marca la casilla **"Add python.exe to PATH"**.
3. Abre **PowerShell** y comprueba:

   ```powershell
   py --version
   ```

## 2. Instalar Git (opcional)

Si vas a clonar el repositorio con Git, instala Git para Windows. Si no, en GitHub usa **Code → Download ZIP** y descomprime el archivo.

## 3. Crear el entorno e instalar

En PowerShell, dentro de la carpeta del repositorio:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
python -m dataton --help
```

Si PowerShell no deja activar el entorno ("la ejecución de scripts está deshabilitada"), ejecuta esto una sola vez y vuelve a intentar:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

En la consola clásica (`cmd.exe`), el entorno se activa con `.venv\Scripts\activate.bat`.

## 4. Comprobar que todo funciona

```powershell
python -m dataton demo
```

Debe terminar con `OK`.

## 5. Comandos frecuentes

```powershell
python -m dataton validar paquetes\D1-base-digital
python -m dataton scorecard paquetes\D1-base-digital
python -m dataton nivel paquetes\D1-base-digital
python -m dataton verificar-privacidad paquetes
```

Las rutas pueden escribirse con `\` o con `/`.

## Problemas frecuentes

| Problema | Solución |
|---|---|
| `python` no se reconoce | Usa `py` en lugar de `python`, o reinstala Python marcando "Add python.exe to PATH" |
| Caracteres raros en la consola | Ejecuta `chcp 65001` antes de los comandos, o usa Windows Terminal |
| `pip` no encuentra los paquetes | Comprueba que el entorno esté activado: el indicador debe empezar con `(.venv)` |
