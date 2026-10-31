"""Streamlit application for the CasaCerca prototype."""

from __future__ import annotations

import os
from datetime import date, time
from pathlib import Path

import pandas as pd
import streamlit as st
from vosk import Model

from app_helpers import (
    filter_available_providers,
    filter_nearby_providers,
    transcribe_wav,
)
from server import PROVIDERS

SAN_SALVADOR = (13.6929, -89.2182)
PROVIDER_RADIUS_KM = 10
DEFAULT_VOSK_MODEL = Path(__file__).parent / "models" / "vosk-model-small-es-0.42"

st.set_page_config(page_title="CasaCerca", page_icon="⌂", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background: #fcfaf5; color: #20342d; }
    h1, h2, h3 { color: #20342d; }
    [data-testid="stHeader"] { background: rgba(252, 250, 245, .9); }
    .casa-subtitle { color: #64716b; margin-top: -1rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

_LOCATION_BUTTON = st.components.v2.component(
    "housekeeper.location_button",
    html="""
    <button id="location-button" type="button">
      Presiona aquí para compartir tu ubicación actual
    </button>
    """,
    css="""
    button {
      align-items: center;
      background: var(--st-primary-color, #ff4b4b);
      border: 1px solid transparent;
      border-radius: var(--st-button-radius, 0.5rem);
      color: #fff;
      cursor: pointer;
      display: inline-flex;
      font: 600 14px var(--st-font, sans-serif);
      justify-content: center;
      min-height: 2.5rem;
      padding: 0.5rem 1rem;
      transition: filter 120ms ease;
    }
    button:hover:not(:disabled) {
      filter: brightness(0.92);
    }
    button:focus-visible {
      outline: 2px solid var(--st-primary-color, #ff4b4b);
      outline-offset: 2px;
    }
    button:disabled {
      cursor: wait;
      opacity: 0.75;
    }
    """,
    js="""
    export default function (component) {
      const { parentElement, setTriggerValue } = component
      const button = parentElement.querySelector("#location-button")
      if (!button) return

      button.onclick = () => {
        button.disabled = true
        button.textContent = "Obteniendo ubicación..."

        if (!navigator.geolocation) {
          setTriggerValue("location", {
            error: "unsupported",
            message: "Este navegador no permite obtener la ubicación.",
          })
          return
        }

        navigator.geolocation.getCurrentPosition(
          (position) => {
            setTriggerValue("location", {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            })
          },
          (error) => {
            setTriggerValue("location", {
              error: error.code,
              message: error.message,
            })
          },
          { enableHighAccuracy: true, timeout: 10000 },
        )
      }
    }
    """,
)


def get_vosk_model() -> Model:
    model_path = Path(os.environ.get("VOSK_MODEL_PATH", str(DEFAULT_VOSK_MODEL)))
    if not model_path.is_dir():
        raise FileNotFoundError(
            f"No se encontró el modelo local de Vosk en {model_path}. "
            "Descarga y extrae el modelo español indicado en README.md."
        )
    return Model(str(model_path))


@st.cache_resource
def load_vosk_model() -> Model:
    return get_vosk_model()


def render_map(providers: list[dict], latitude: float, longitude: float, has_location: bool) -> None:
    map_points = []
    for provider in providers:
        map_points.append(
            {
                "lat": float(provider["lat"]),
                "lng": float(provider["lng"]),
                "color": "#e9725b",
                "size": 50,
            }
        )

    if has_location:
        map_points.append({
            "lat": latitude,
            "lng": longitude,
            "color": "#2259b0",
            "size": 120,
        })

    st.map(
        pd.DataFrame(map_points, columns=["lat", "lng", "color", "size"]),
        latitude="lat",
        longitude="lng",
        color="color",
        size="size",
        zoom=12 if has_location else 11,
        height=420,
    )
    if has_location:
        st.caption("Puntos coral: proveedores cercanos. Punto azul: tu ubicación.")
    else:
        st.caption("Puntos coral: proveedores del prototipo en San Salvador.")


def render_provider_cards(providers: list[dict]) -> None:
    for provider in providers:
        with st.container(border=True):
            image_column, details_column, price_column = st.columns([1, 5, 1])
            with image_column:
                st.image(provider["photo"], width=72)
            with details_column:
                st.markdown(f"**{provider['name']}** · ★ {provider['rating']}")
                st.write(
                    f"{provider['area']} · {' · '.join(provider['services'])}"
                )
                st.caption(
                    f"Disponible {', '.join(provider['days'])} · "
                    f"{provider['start']}–{provider['end']}"
                )
            with price_column:
                st.markdown(f"**${provider['fee']}/hora**")


def transcribe_audio(audio_bytes: bytes) -> str | None:
    try:
        return transcribe_wav(audio_bytes, load_vosk_model())
    except FileNotFoundError as error:
        st.error(str(error))
    except ValueError as error:
        st.error(f"No se pudo procesar el audio: {error}")
    except (OSError, RuntimeError) as error:
        st.error(f"No se pudo cargar el modelo local de transcripción: {error}")
    return None


def render_audio_input() -> bytes | None:
    st.subheader("Entrada por audio")

    microphone_consent = st.checkbox(
        "Doy permiso para usar el micrófono.",
        key="microphone_consent",
    )
    st.caption(
        "La transcripción solo considera los primeros 15 segundos; el contenido "
        "posterior se descarta. Menciona una referencia del lugar, la fecha y la "
        "hora. Si falta la fecha o la hora, la transcripción se consulta con el "
        "buscador RAG."
    )

    st.markdown(
        """
        <style>
        div[role="radiogroup"] label p {
            color: gray !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    input_mode = st.radio(
        "Cómo ingresar el audio",
        ("Subir archivo WAV", "Grabar con el micrófono"),
        horizontal=True,
        key="audio_input_mode",
    )
    audio_bytes = None
    if input_mode == "Subir archivo WAV":
        uploaded_audio = st.file_uploader(
            "Selecciona un archivo WAV",
            type=["wav"],
            key="uploaded_audio",
        )
        if uploaded_audio is not None:
            audio_bytes = uploaded_audio.getvalue()
    elif microphone_consent:
        recorded_audio = st.audio_input(
            "Graba un audio para transcribirlo",
            sample_rate=16000,
            key="recorded_audio",
        )
        if recorded_audio is not None:
            audio_bytes = recorded_audio.getvalue()
    else:
        st.info("Concede permiso para usar el micrófono. En el checkbox de arriba")

    transcript = st.session_state.get("audio_transcript")
    if transcript:
        st.markdown("**Transcripción del audio**")
        st.write(transcript)
    return audio_bytes


def render_app() -> None:
    st.title("CasaCerca")
    st.markdown("Encuentra servicios de limpieza para tu hogar.")

    st.subheader("Ubicación")
    location_result = _LOCATION_BUTTON(
        key="location_button",
        on_location_change=lambda: None,
    ).location
    location = (
        location_result
        if isinstance(location_result, dict)
        else None
    )
    location_error = location.get("error") if location else None
    has_location = (
        isinstance(location, dict)
        and isinstance(location.get("latitude"), (int, float))
        and isinstance(location.get("longitude"), (int, float))
        and not location_error
    )

    audio_bytes = render_audio_input()

    if has_location:
        latitude = float(location["latitude"])
        longitude = float(location["longitude"])
        try:
            geo_providers = filter_nearby_providers(
                PROVIDERS,
                latitude,
                longitude,
                PROVIDER_RADIUS_KM,
            )
        except ValueError as error:
            st.error(f"No se pudieron filtrar los proveedores: {error}")
            geo_providers = []
        st.caption("El mapa muestra proveedores a 10 km o menos de tu ubicación.")
    else:
        latitude, longitude = SAN_SALVADOR
        geo_providers = list(PROVIDERS)

    with st.form("availability_filters"):
        date_column, time_column = st.columns(2)
        with date_column:
            selected_date: date | None = st.date_input(
                "Fecha",
                value=None,
                format="DD/MM/YYYY",
            )
        with time_column:
            selected_time: time | None = st.time_input(
                "Hora de inicio",
                value=None,
            )
        search_submitted = st.form_submit_button(
            "Buscar disponibilidad",
            type="primary",
        )

    if "availability_searched" not in st.session_state:
        st.session_state["availability_searched"] = False
    if search_submitted:
        st.session_state.pop("audio_rag_answer", None)
        st.session_state.pop("audio_rag_providers", None)
        if selected_date is not None and selected_time is not None:
            st.session_state["availability_searched"] = True
            st.session_state["availability_date"] = selected_date
            st.session_state["availability_time"] = selected_time
        elif audio_bytes is None:
            st.warning(
                "Completa la fecha y la hora, o sube un archivo WAV / graba un "
                "audio para buscar con RAG."
            )
        else:
            transcript = transcribe_audio(audio_bytes)
            if transcript == "":
                st.info("No se reconocieron palabras en los primeros 15 segundos.")
            elif transcript is not None:
                st.session_state["audio_transcript"] = transcript
                st.markdown("**Transcripción usada para esta búsqueda**")
                st.write(transcript)
                try:
                    from google.genai.errors import APIError
                    from langchain_google_genai.chat_models import (
                        GoogleGenerativeAIError,
                    )
                    from rag_app import buscar_resultados_con_rag

                    rag_result = buscar_resultados_con_rag(transcript)
                    st.session_state["audio_rag_answer"] = rag_result.answer
                    st.session_state["audio_rag_providers"] = rag_result.providers
                except (ImportError, RuntimeError, ValueError) as error:
                    st.error(f"No se pudo ejecutar la búsqueda RAG: {error}")
                except (APIError, GoogleGenerativeAIError) as error:
                    st.error(f"Gemini no pudo completar la búsqueda RAG: {error}")

    if st.session_state.get("audio_rag_answer"):
        st.subheader("Resultados de la búsqueda por audio")
        st.write(st.session_state["audio_rag_answer"])
    if "audio_rag_providers" in st.session_state:
        rag_providers = st.session_state["audio_rag_providers"]
        st.subheader("Proveedoras relacionadas con tu búsqueda por audio")
        if rag_providers:
            render_provider_cards(rag_providers)
        else:
            st.info("El RAG no recuperó proveedoras para mostrar.")

    if st.session_state["availability_searched"]:
        geo_providers = filter_available_providers(
            geo_providers,
            st.session_state.get("availability_date"),
            st.session_state.get("availability_time"),
        )

    st.subheader(f"{len(geo_providers)} proveedores disponibles")
    render_map(geo_providers, latitude, longitude, has_location)
    if not geo_providers:
        st.info("No hay proveedores disponibles en esta ubicación y horario.")
    else:
        render_provider_cards(geo_providers)

    st.divider()


render_app()
