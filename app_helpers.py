"""Pure helpers for provider filtering and temporary audio preparation."""

from __future__ import annotations

from datetime import date, time
from io import BytesIO
import json
import math
import wave
from typing import Any, Iterable

EARTH_RADIUS_KM = 6371.0088
MAX_AUDIO_SECONDS = 15
WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")
def _validate_coordinates(latitude: float, longitude: float) -> None:
    if not math.isfinite(latitude) or not -90 <= latitude <= 90:
        raise ValueError("La latitud debe estar entre -90 y 90 grados.")
    if not math.isfinite(longitude) or not -180 <= longitude <= 180:
        raise ValueError("La longitud debe estar entre -180 y 180 grados.")


def distance_km(
    latitude_a: float,
    longitude_a: float,
    latitude_b: float,
    longitude_b: float,
) -> float:
    """Return the great-circle distance between two coordinate pairs."""
    _validate_coordinates(latitude_a, longitude_a)
    _validate_coordinates(latitude_b, longitude_b)

    lat_a = math.radians(latitude_a)
    lat_b = math.radians(latitude_b)
    lat_delta = lat_b - lat_a
    lon_delta = math.radians(longitude_b - longitude_a)

    haversine = (
        math.sin(lat_delta / 2) ** 2
        + math.cos(lat_a) * math.cos(lat_b) * math.sin(lon_delta / 2) ** 2
    )
    central_angle = 2 * math.asin(math.sqrt(min(1.0, haversine)))
    return EARTH_RADIUS_KM * central_angle


def filter_nearby_providers(
    providers: Iterable[dict[str, Any]],
    latitude: float,
    longitude: float,
    radius_km: float = 10,
) -> list[dict[str, Any]]:
    """Keep existing providers within the inclusive radius of the user."""
    _validate_coordinates(latitude, longitude)
    if not math.isfinite(radius_km) or radius_km < 0:
        raise ValueError("El radio debe ser un número no negativo.")

    nearby = []
    for provider in providers:
        try:
            provider_latitude = float(provider["lat"])
            provider_longitude = float(provider["lng"])
        except (KeyError, TypeError, ValueError) as error:
            provider_name = provider.get("name", "sin nombre")
            raise ValueError(
                f"El proveedor {provider_name} no tiene coordenadas válidas."
            ) from error

        if distance_km(
            latitude,
            longitude,
            provider_latitude,
            provider_longitude,
        ) <= radius_km:
            nearby.append(provider)
    return nearby


def filter_available_providers(
    providers: Iterable[dict[str, Any]],
    selected_date: date | None,
    selected_time: time | None,
) -> list[dict[str, Any]]:
    """Preserve the prototype's date-and-time availability filter behavior."""
    provider_list = list(providers)
    if selected_date is None or selected_time is None:
        return provider_list

    weekday = WEEKDAYS[selected_date.weekday()]
    return [
        provider
        for provider in provider_list
        if weekday in provider["days"]
        and provider["start"] <= selected_time.strftime("%H:%M") < provider["end"]
    ]


def truncate_wav(
    audio_bytes: bytes,
    max_seconds: int = MAX_AUDIO_SECONDS,
) -> bytes:
    """Return an in-memory WAV containing no more than the first N seconds."""
    if max_seconds <= 0:
        raise ValueError("La duración máxima debe ser mayor que cero.")

    try:
        with wave.open(BytesIO(audio_bytes), "rb") as source:
            if source.getcomptype() != "NONE":
                raise ValueError("El audio debe estar en formato WAV PCM.")
            if source.getnchannels() != 1 or source.getsampwidth() != 2:
                raise ValueError("El audio debe ser PCM mono de 16 bits.")
            if source.getframerate() <= 0:
                raise ValueError("El audio tiene una frecuencia de muestreo inválida.")

            frame_count = min(
                source.getnframes(),
                source.getframerate() * max_seconds,
            )
            frames = source.readframes(frame_count)
            parameters = source.getparams()
    except (EOFError, wave.Error) as error:
        raise ValueError("No se pudo leer el audio como un archivo WAV válido.") from error

    output = BytesIO()
    with wave.open(output, "wb") as target:
        target.setparams(parameters)
        target.writeframes(frames)
    return output.getvalue()


def transcribe_wav(audio_bytes: bytes, model: Any) -> str:
    """Transcribe a WAV using the supplied local Vosk model."""
    from vosk import KaldiRecognizer

    shortened_audio = truncate_wav(audio_bytes)
    with wave.open(BytesIO(shortened_audio), "rb") as wav_file:
        recognizer = KaldiRecognizer(model, wav_file.getframerate())
        recognizer.AcceptWaveform(wav_file.readframes(wav_file.getnframes()))
    result = json.loads(recognizer.FinalResult())
    return result.get("text", "").strip()
