import math
from datetime import date, time
from io import BytesIO
import json
import wave
import unittest
from unittest.mock import patch

from app_helpers import (
    distance_km,
    filter_available_providers,
    filter_nearby_providers,
    transcribe_wav,
    truncate_wav,
)


class ProviderFilteringTests(unittest.TestCase):
    def test_distance_is_zero_for_same_coordinates(self):
        self.assertEqual(distance_km(13.7, -89.2, 13.7, -89.2), 0)

    def test_filter_includes_provider_at_or_inside_radius(self):
        providers = [
            {"id": 1, "name": "near", "lat": 0.0, "lng": 0.0},
            {"id": 2, "name": "far", "lat": 0.0, "lng": 0.2},
        ]
        ten_km_latitude = math.degrees(10 / 6371.0088)

        nearby = filter_nearby_providers(
            providers,
            latitude=0,
            longitude=0,
            radius_km=10,
        )
        boundary = filter_nearby_providers(
            [{"id": 3, "name": "edge", "lat": ten_km_latitude, "lng": 0}],
            latitude=0,
            longitude=0,
            radius_km=10,
        )

        self.assertEqual([provider["id"] for provider in nearby], [1])
        self.assertEqual([provider["id"] for provider in boundary], [3])

    def test_invalid_provider_coordinates_are_reported(self):
        with self.assertRaisesRegex(ValueError, "coordenadas válidas"):
            filter_nearby_providers([{"name": "sin coordenadas"}], 0, 0)

    def test_invalid_user_coordinates_are_reported(self):
        with self.assertRaisesRegex(ValueError, "latitud"):
            filter_nearby_providers([], 91, 0)

    def test_date_and_time_filters_keep_prototype_behavior(self):
        providers = [
            {"id": 1, "days": ["Mon"], "start": "08:00", "end": "16:00"},
            {"id": 2, "days": ["Tue"], "start": "08:00", "end": "16:00"},
        ]

        self.assertEqual(filter_available_providers(providers, None, time(9)), providers)
        self.assertEqual(
            [p["id"] for p in filter_available_providers(
                providers, date(2026, 10, 26), time(9)
            )],
            [1],
        )
        self.assertEqual(
            filter_available_providers(providers, date(2026, 10, 26), time(16)),
            [],
        )


class AudioPreparationTests(unittest.TestCase):
    @staticmethod
    def make_wav(seconds: int) -> bytes:
        stream = BytesIO()
        with wave.open(stream, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(16000)
            wav_file.writeframes(b"\0\0" * (16000 * seconds))
        return stream.getvalue()

    def test_audio_is_truncated_to_first_fifteen_seconds(self):
        shortened = truncate_wav(self.make_wav(20))
        with wave.open(BytesIO(shortened), "rb") as wav_file:
            self.assertEqual(wav_file.getnframes(), 16000 * 15)

    def test_short_audio_is_kept_without_extension(self):
        shortened = truncate_wav(self.make_wav(5))
        with wave.open(BytesIO(shortened), "rb") as wav_file:
            self.assertEqual(wav_file.getnframes(), 16000 * 5)

    def test_invalid_audio_is_reported(self):
        with self.assertRaisesRegex(ValueError, "WAV válido"):
            truncate_wav(b"not audio")

    def test_transcription_receives_only_first_fifteen_seconds(self):
        class FakeRecognizer:
            received_frames = b""

            def AcceptWaveform(self, frames):
                self.received_frames = frames

            def FinalResult(self):
                return json.dumps({"text": "  texto reconocido  "})

        recognizer = FakeRecognizer()
        with patch("vosk.KaldiRecognizer", return_value=recognizer):
            transcript = transcribe_wav(self.make_wav(20), model=object())

        self.assertEqual(len(recognizer.received_frames), 16000 * 15 * 2)
        self.assertEqual(transcript, "texto reconocido")
