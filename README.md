# Prototipo de CasaCerca

Este repositorio contiene un prototipo React + Python para encontrar servicios de limpieza en San Salvador. La adaptación objetivo usa Streamlit y conserva los filtros manuales existentes de fecha y hora.

La aplicación Streamlit abre directamente en la pantalla principal y no requiere inicio de sesión.

## Requisitos implementados

- Usa la lista existente `PROVIDERS` de `server.py` y muestra los proveedores a 10 km o menos de la ubicación actual del usuario. No inventa proveedores ni fija la ubicación del usuario.
- Solicita permiso de ubicación. Si se deniega o no se obtiene la ubicación, muestra el mapa actual de San Salvador.
- Muestra un mapa geográfico real con marcadores para los proveedores y, cuando está disponible, la ubicación del usuario. No dibuja un círculo de 10 km. Los mosaicos del mapa los sirve CARTO y requieren conexión a Internet.
- Conserva sin cambios la búsqueda por fecha y hora cuando ambos campos están completos. Si falta alguno, permite buscar con el RAG existente a partir de la transcripción, sin modificar los filtros ni el mapa.
- Permite subir un WAV o grabar audio con consentimiento explícito; solo considera los primeros 15 segundos para transcribir y descarta el contenido posterior.
- Indica que el audio debe incluir referencia del lugar, fecha y hora. Acepta audio en español sin validar el idioma.
- Transcribe localmente con Vosk y muestra el texto reconocido. Si falta fecha u hora, consulta el RAG existente y muestra su respuesta separada.
- No guarda el audio en archivos; permanece solo en la sesión de Streamlit para poder enviarlo en la búsqueda.
- Sin permiso del micrófono, no graba audio; permite subir un archivo WAV.
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

## Módulo RAG experimental

`rag_app.py` contiene la cadena RAG utilizada como alternativa solo cuando falta la fecha o la hora. Usa la lista existente `PROVIDERS` y Gemini; la consulta envía texto a la API de Google. La respuesta y las proveedoras recuperadas se muestran en una sección separada, sin alterar los filtros manuales ni el mapa. El flujo de disponibilidad por fecha y hora no usa RAG.

Instala sus dependencias adicionales con `python -m pip install -r requirements-rag.txt`. `rag_app.py` lee `GEMINI_API_KEY` desde `.env` o desde una variable de entorno. Usa `.env.example` solo como plantilla, con un marcador de posición, nunca para guardar una clave real. Después, crea e invoca la cadena desde otro módulo:

```python
from rag_app import crear_cadena_rag

cadena_rag = crear_cadena_rag()
respuesta = cadena_rag.invoke("¿Quién ofrece limpieza general?")
```

La cadena se construye al llamar a `crear_cadena_rag`, no al importar el módulo. La dependencia con Gemini se mantiene separada de `requirements.txt` para no añadirla a la instalación normal de CasaCerca.

## Prototipo anterior

`server.py` todavía contiene el servidor HTTP del prototipo original, incluida su validación de sesión. La aplicación Streamlit no usa el inicio de sesión del prototipo y solo importa de `server.py` la lista `PROVIDERS`.

Consulta [docs/constitution.md](docs/constitution.md) y [specs/](specs/) para el alcance detallado y los criterios de aceptación.
