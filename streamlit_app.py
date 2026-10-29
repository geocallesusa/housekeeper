"""Streamlit application for the CasaCerca prototype."""

from __future__ import annotations

import os
from datetime import date, time
from html import escape
import math
from pathlib import Path

import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from vosk import Model

from app_helpers import (
    distance_km,
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
    map_radius_km = PROVIDER_RADIUS_KM
    if not has_location and providers:
        map_radius_km = max(
            distance_km(
                latitude,
                longitude,
                float(provider["lat"]),
                float(provider["lng"]),
            )
            for provider in providers
        ) * 1.15
    map_radius_km = max(map_radius_km, 1)

    longitude_scale = 111.32 * max(math.cos(math.radians(latitude)), 0.01)
    marker_svg = []
    for provider in providers:
        x = 500 + (
            (float(provider["lng"]) - longitude) * longitude_scale / map_radius_km * 210
        )
        y = 280 - (
            (float(provider["lat"]) - latitude) * 111.32 / map_radius_km * 210
        )
        description = escape(
            f"{provider['name']} · {provider['area']} · ${provider['fee']}/hora"
        )
        marker_svg.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="#e9725b" '
            f'stroke="#fff" stroke-width="3"><title>{description}</title></circle>'
        )

    radius_svg = ""
    user_marker_svg = ""
    if has_location:
        radius_svg = """
        <circle cx="500" cy="280" r="210" fill="#2e715d" fill-opacity=".08"
          stroke="#2e715d" stroke-opacity=".65" stroke-width="2"/>
        <circle cx="500" cy="280" r="105" fill="none"
          stroke="#2e715d" stroke-opacity=".25" stroke-dasharray="5 7"/>
        <text x="712" y="276" class="map-label">10 km</text>
        """
        user_marker_svg = """
        <circle cx="500" cy="280" r="12" fill="#2259b0"
          stroke="#fff" stroke-width="4"><title>Tu ubicación</title></circle>
        """

    map_heading = (
        "Proveedores a 10 km o menos"
        if has_location
        else "San Salvador · ubicación de respaldo"
    )
    map_svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 560"
      role="img" aria-label="{map_heading}">
      <style>
        .map-label {{ font: 600 16px sans-serif; fill: #40544b; }}
        .map-heading {{ font: 700 20px sans-serif; fill: #20342d; }}
        .map-legend {{ font: 14px sans-serif; fill: #40544b; }}
      </style>
      <rect width="1000" height="560" rx="18" fill="#eaf0e8"/>
      <path d="M0 140H1000M0 280H1000M0 420H1000M250 0V560M500 0V560M750 0V560"
        stroke="#fff" stroke-opacity=".7" stroke-width="2"/>
      <text x="40" y="48" class="map-heading">{escape(map_heading)}</text>
      {radius_svg}
      {''.join(marker_svg)}
      {user_marker_svg}
      <circle cx="44" cy="510" r="8" fill="#e9725b"/>
      <text x="62" y="515" class="map-legend">Profesionales</text>
      {'<circle cx="220" cy="510" r="8" fill="#2259b0"/><text x="238" y="515" class="map-legend">Tu ubicación</text>' if has_location else ''}
    </svg>
    """
    st.iframe(map_svg, height=380)


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
    st.caption("Presiona el botón de ubicación para compartir tu posición actual.")
    location = streamlit_geolocation()
    has_location = (
        isinstance(location, dict)
        and isinstance(location.get("latitude"), (int, float))
        and isinstance(location.get("longitude"), (int, float))
    )

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
        st.info(
            "No se obtuvo la ubicación. Se muestra el mapa actual de San Salvador "
            "con los proveedores del prototipo."
        )

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
    render_audio_input()


render_app()
