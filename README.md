# Prototipo de CasaCerca

Este repositorio contiene un prototipo React + Python para encontrar servicios de limpieza en San Salvador. La adaptación objetivo usa Streamlit y conserva los filtros manuales existentes de fecha y hora.

La aplicación Streamlit abre directamente en la pantalla principal y no requiere inicio de sesión.

## Requisitos implementados

- Usa la lista existente `PROVIDERS` de `server.py` y muestra los proveedores a 10 km o menos de la ubicación actual del usuario. No inventa proveedores ni fija la ubicación del usuario.
- Solicita permiso de ubicación. Si se deniega o no se obtiene la ubicación, muestra el mapa actual de San Salvador.
- Muestra un mapa geográfico real con marcadores para los proveedores y, cuando está disponible, la ubicación del usuario. No dibuja un círculo de 10 km. Los mosaicos del mapa los sirve CARTO y requieren conexión a Internet.
- Conserva los filtros manuales de fecha y hora. La entrada y transcripción de audio no los activan, reemplazan ni modifican.
- Ofrece entrada de audio mediante micrófono, con consentimiento explícito; solo considera los primeros 15 segundos para la transcripción y descarta el contenido posterior.
- Indica que el audio debe incluir referencia del lugar, fecha y hora. Acepta audio en español sin validar el idioma.
- Transcribe localmente con Vosk y muestra el texto reconocido. La transcripción no ejecuta búsquedas.
- No guarda el audio en archivos ni lo conserva después de enviar el formulario. La captura se limita a la sesión de Streamlit.
- Si no se concede permiso al micrófono, permite ingresar texto en el campo alternativo.
- Usa bibliotecas de código abierto.

## Preparación local

Se requiere Python 3.10 o posterior y Streamlit 1.50 o posterior. En PowerShell, crea y activa un entorno virtual e instala las dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Descarga el modelo pequeño de español de Vosk desde la [lista oficial de modelos](https://alphacephei.com/vosk/models) y extrae el directorio `vosk-model-small-es-0.42` en `models\vosk-model-small-es-0.42`. El modelo no se incluye en el repositorio. También puedes indicar su ubicación mediante la variable de entorno `VOSK_MODEL_PATH`.

## Ejecutar desde la terminal de Visual Studio Code

Abre la carpeta del proyecto en Visual Studio Code y selecciona **Terminal > Nueva terminal**. Asegúrate de que la terminal esté ubicada en la carpeta `housekeeper`. Después de completar la preparación local, ejecuta:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

La ubicación y el micrófono requieren permiso del navegador. En producción, el sitio debe servirse mediante HTTPS; `localhost` es válido para desarrollo local.

## Prototipo anterior

`server.py` todavía contiene el servidor HTTP del prototipo original, incluida su validación de sesión. La aplicación Streamlit no usa el inicio de sesión del prototipo y solo importa de `server.py` la lista `PROVIDERS`.

Consulta [docs/constitution.md](docs/constitution.md) y [specs/](specs/) para el alcance detallado y los criterios de aceptación.
