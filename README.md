# CasaCerca

Prototipo Streamlit para encontrar servicios de limpieza. La aplicación abre sin inicio de sesión.

## Preparación y ejecución

Requiere Python 3.10 o posterior. En la terminal de Visual Studio Code, desde la carpeta del proyecto, ejecuta:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-rag.txt
```

Descarga el modelo pequeño de español de [Vosk](https://alphacephei.com/vosk/models) y extrae `vosk-model-small-es-0.42` en `models\vosk-model-small-es-0.42`. Luego inicia la aplicación:

```powershell
.\.venv\Scripts\python.exe -m streamlit run streamlit_app.py
```

## Configurar Gemini

Crea `.streamlit\secrets.toml` y añade tu clave de Gemini:

```toml
GEMINI_API_KEY = "tu_clave_de_gemini"
```

Reemplaza el texto de ejemplo por tu clave real. El archivo está excluido de Git; no compartas ni subas la clave al repositorio. La consulta RAG usa Gemini cuando falta la fecha o la hora.

## Funcionalidad

- Muestra proveedores de `PROVIDERS` a 10 km o menos de la ubicación del usuario; si no se obtiene, usa el mapa de San Salvador. El mapa real requiere conexión a Internet.
- Conserva la búsqueda por fecha y hora. Si falta uno de esos campos, permite consultar el RAG con audio.
- Acepta WAV o grabación con permiso del micrófono, transcribe localmente con Vosk y limita la transcripción a los primeros 15 segundos.
- No guarda el audio. El modelo de Vosk y el archivo de secretos no se incluyen en el repositorio.

La ubicación y el micrófono requieren permisos del navegador. En producción, usa HTTPS.
