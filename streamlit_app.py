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


def render_audio_input() -> None:
    st.subheader("Entrada por audio")
    st.caption(
        "La transcripción solo considera los primeros 15 segundos; el contenido "
        "posterior se descarta. Menciona una referencia del lugar, la fecha y la "
        "hora. El audio se usa solo para mostrar su transcripción; no inicia una búsqueda."
    )
    st.text_input(
        "Entrada de texto alternativa",
        key="text_search_input",
        help="Si no concedes permiso al micrófono, puedes ingresar texto aquí.",
    )

    microphone_consent = st.checkbox(
        "Doy permiso para usar el micrófono.",
        key="microphone_consent",
    )
    if not microphone_consent:
        st.info("Sin este permiso, solo está disponible la entrada de texto.")
        return

    with st.form("audio_form", clear_on_submit=True):
        audio = st.audio_input(
            "Graba un audio para transcribirlo",
            sample_rate=16000,
        )
        submitted = st.form_submit_button("Transcribir audio")

    if not submitted:
        return
    if audio is None:
        st.warning("Graba un audio antes de solicitar la transcripción.")
        return

    try:
        transcript = transcribe_wav(audio.getvalue(), load_vosk_model())
    except FileNotFoundError as error:
        st.error(str(error))
        return
    except ValueError as error:
        st.error(f"No se pudo procesar el audio: {error}")
        return
    except (OSError, RuntimeError) as error:
        st.error(f"No se pudo cargar el modelo local de transcripción: {error}")
        return

    if transcript:
        st.markdown("**Transcripción del audio**")
        st.write(transcript)
    else:
        st.info("No se reconocieron palabras en los primeros 15 segundos.")


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

    render_audio_input()

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
        if location_error:
            st.info(
                "No se obtuvo la ubicación. Se muestra el mapa actual de San Salvador "
                "con los proveedores del prototipo."
            )
        else:
            st.caption("Comparte tu ubicación para ver los proveedores cercanos.")

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
        st.session_state["availability_searched"] = True
        st.session_state["availability_date"] = selected_date
        st.session_state["availability_time"] = selected_time

    if st.session_state["availability_searched"]:
        geo_providers = filter_available_providers(
            geo_providers,
            st.session_state.get("availability_date"),
            st.session_state.get("availability_time"),
        )

    st.subheader(f"{len(geo_providers)} profesionales disponibles")
    render_map(geo_providers, latitude, longitude, has_location)
    if not geo_providers:
        st.info("No hay proveedores disponibles en esta ubicación y horario.")
    else:
        for provider in geo_providers:
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

    st.divider()

render_app()
