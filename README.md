# Prototipo de CasaCerca

Este repositorio contiene un prototipo React + Python para encontrar servicios de limpieza en San Salvador. La adaptación objetivo usa Streamlit y conserva los filtros manuales existentes de fecha y hora.

## Requisitos implementados

- Usa la lista existente `PROVIDERS` de `server.py` y muestra los proveedores a 10 km o menos de la ubicación actual del usuario. No inventa proveedores ni fija la ubicación del usuario.
- Solicita permiso de ubicación. Si se deniega o no se obtiene la ubicación, muestra el mapa actual de San Salvador.
- Dibuja el mapa como un esquema SVG local, sin solicitar mosaicos a un servicio externo.
- Conserva los filtros manuales de fecha y hora. La entrada y transcripción de audio no los activan, reemplazan ni modifican.
- Ofrece entrada de audio mediante micrófono, con consentimiento explícito; solo considera los primeros 15 segundos para la transcripción y descarta el contenido posterior.
- Indica que el audio debe incluir referencia del lugar, fecha y hora. Acepta audio en español sin validar el idioma.
- Transcribe localmente con Vosk y muestra el texto reconocido. La transcripción no ejecuta búsquedas.
- No guarda el audio en archivos ni lo conserva después de enviar el formulario. La captura se limita a la sesión de Streamlit.
- Si no se concede permiso al micrófono, permite ingresar texto en el campo alternativo.
- Usa bibliotecas de código abierto.

## Preparación local

Se requiere Python 3.10 o posterior. En PowerShell, crea y activa un entorno virtual e instala las dependencias:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Descarga el modelo pequeño de español de Vosk desde la [lista oficial de modelos](https://alphacephei.com/vosk/models) y extrae el directorio `vosk-model-small-es-0.42` en `models\vosk-model-small-es-0.42`. El modelo no se incluye en el repositorio. También puedes indicar su ubicación mediante la variable de entorno `VOSK_MODEL_PATH`.

Inicia la aplicación:

```powershell
streamlit run streamlit_app.py
```

La ubicación y el micrófono requieren permiso del navegador. En producción, el sitio debe servirse mediante HTTPS; `localhost` es válido para desarrollo local.

## Prototipo anterior

`server.py` todavía contiene el servidor HTTP del prototipo original. La aplicación adaptada a Streamlit utiliza `streamlit_app.py` y toma de `server.py` los datos `PROVIDERS` y la validación de la sesión de demostración.

Consulta [docs/constitution.md](docs/constitution.md) y [specs/](specs/) para el alcance detallado y los criterios de aceptación.
