#!/usr/bin/env python3
"""Tiny, dependency-free server for the CasaCerca prototype."""
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import secrets
from urllib.parse import urlparse

ROOT = Path(__file__).parent

USERS = {
    "admin@geovany.com": {
        "email": "admin@geovany.com",
        "name": "Geovany Calles",
        "role": "admin",
        "password": "housekeeper123",
    }
}
SESSIONS = {}
SESSION_COOKIE = "session"

PROVIDERS = [
    {"id": 1, "name": "Ana Martínez", "photo": "https://i.pravatar.cc/240?img=47", "fee": 10, "rating": 4.9, "area": "Escalón", "lat": 13.7046, "lng": -89.2369, "days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "start": "08:00", "end": "16:00", "services": ["Limpieza general", "Plancha"]},
    {"id": 2, "name": "Rosa Hernández", "photo": "https://i.pravatar.cc/240?img=45", "fee": 9, "rating": 4.8, "area": "San Benito", "lat": 13.6998, "lng": -89.2385, "days": ["Mon", "Wed", "Fri", "Sat"], "start": "09:00", "end": "17:00", "services": ["Limpieza profunda", "Cocina"]},
    {"id": 3, "name": "María López", "photo": "https://i.pravatar.cc/240?img=49", "fee": 12, "rating": 5.0, "area": "Santa Elena", "lat": 13.6768, "lng": -89.2453, "days": ["Tue", "Thu", "Fri", "Sat"], "start": "07:00", "end": "15:00", "services": ["Limpieza general", "Lavandería"]},
    {"id": 4, "name": "Carla Ramírez", "photo": "https://i.pravatar.cc/240?img=32", "fee": 11, "rating": 4.7, "area": "Colonia San Francisco", "lat": 13.6929, "lng": -89.2193, "days": ["Mon", "Tue", "Thu", "Sun"], "start": "08:00", "end": "18:00", "services": ["Limpieza profunda", "Mascotas"]},
    {"id": 5, "name": "Sofía Castillo", "photo": "https://i.pravatar.cc/240?img=44", "fee": 13, "rating": 4.9, "area": "Antiguo Cuscatlán", "lat": 13.6635, "lng": -89.2531, "days": ["Mon", "Tue", "Wed", "Thu", "Fri"], "start": "10:00", "end": "18:00", "services": ["Limpieza general", "Organización"]},
    {"id": 6, "name": "Patricia Gómez", "photo": "https://i.pravatar.cc/240?img=38", "fee": 10, "rating": 4.8, "area": "Miralvalle", "lat": 13.7189, "lng": -89.2235, "days": ["Tue", "Wed", "Thu", "Fri", "Sat"], "start": "08:00", "end": "16:00", "services": ["Limpieza general", "Ventanas"]},
    {"id": 7, "name": "Verónica Cruz", "photo": "https://i.pravatar.cc/240?img=37", "fee": 8, "rating": 4.6, "area": "Mejicanos", "lat": 13.7341, "lng": -89.2175, "days": ["Mon", "Wed", "Thu", "Sat"], "start": "07:00", "end": "14:00", "services": ["Limpieza básica", "Plancha"]},
    {"id": 8, "name": "Isabel Flores", "photo": "https://i.pravatar.cc/240?img=26", "fee": 14, "rating": 5.0, "area": "San Jacinto", "lat": 13.6800, "lng": -89.1930, "days": ["Mon", "Tue", "Wed", "Fri", "Sat"], "start": "09:00", "end": "17:00", "services": ["Limpieza profunda", "Cocina"]},
    {"id": 9, "name": "Gloria Reyes", "photo": "https://i.pravatar.cc/240?img=42", "fee": 9, "rating": 4.7, "area": "Zona Rosa", "lat": 13.6970, "lng": -89.2320, "days": ["Tue", "Thu", "Fri", "Sat", "Sun"], "start": "08:00", "end": "17:00", "services": ["Limpieza general", "Lavandería"]},
    {"id": 10, "name": "Elena Morales", "photo": "https://i.pravatar.cc/240?img=48", "fee": 11, "rating": 4.9, "area": "Centro Histórico", "lat": 13.6990, "lng": -89.1910, "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], "start": "06:00", "end": "14:00", "services": ["Limpieza básica", "Oficinas"]},
]


def validate_login(email, password):
    if not email or not password:
        return None
    user = USERS.get(email.strip().lower())
    if user and user["password"] == password:
        return {"email": user["email"], "name": user["name"], "role": user["role"]}
    return None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def _read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length) if length else b"{}"
        return json.loads(raw.decode("utf-8") or "{}")

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def _get_session_user(self):
        cookie = self.headers.get("Cookie", "")
        if not cookie:
            return None
        for part in cookie.split(";"):
            key, _, value = part.strip().partition("=")
            if key == SESSION_COOKIE:
                email = SESSIONS.get(value)
                if email and email in USERS:
                    user = USERS[email]
                    return {"email": user["email"], "name": user["name"], "role": user["role"]}
        return None

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/providers":
            self._send_json(200, PROVIDERS)
        elif path == "/api/session":
            self._send_json(200, {"user": self._get_session_user()})
        else:
            super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == "/api/login":
            payload = self._read_json()
            user = validate_login(payload.get("email"), payload.get("password"))
            if not user:
                self._send_json(401, {"error": "Credenciales incorrectas."})
                return
            token = secrets.token_urlsafe(16)
            SESSIONS[token] = user["email"]
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}={token}; HttpOnly; Path=/; SameSite=Lax")
            body = json.dumps({"user": user}).encode("utf-8")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
            return
        if path == "/api/logout":
            cookie = self.headers.get("Cookie", "")
            for part in cookie.split(";"):
                key, _, value = part.strip().partition("=")
                if key == SESSION_COOKIE:
                    SESSIONS.pop(value, None)
            self.send_response(200)
            self.send_header("Set-Cookie", f"{SESSION_COOKIE}=; Max-Age=0; Path=/; HttpOnly; SameSite=Lax")
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True}).encode("utf-8"))
            return
        self.send_response(405)
        self.end_headers()


if __name__ == "__main__":
    print("CasaCerca is running at http://localhost:8000")
    ThreadingHTTPServer(("", 8000), Handler).serve_forever()
