
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any, Callable, Optional

BASE_URL = "https://api.clashroyale.com/v1"


class ClashRoyaleError(Exception):
    """Raised for any failure talking to the API, with a message meant for the user."""


def load_env_file(path: str = ".env") -> None:
    """Load KEY=VALUE lines from a file into os.environ (without overriding existing values).

    Lines that are empty or start with '#' are ignored. If the file does not exist, nothing happens.
    """
    if not os.path.isfile(path):
        return
    with open(path, encoding="utf-8") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


class ClashRoyaleClient:
    """Thin wrapper around the endpoints this project needs: cards, player, battle log."""

    def __init__(
        self,
        token: str,
        base_url: str = BASE_URL,
        timeout: int = 15,
        opener: Optional[Callable[..., Any]] = None,
    ) -> None:
        if not token:
            raise ClashRoyaleError(
                "Falta la llave de la API. Define CR_API_TOKEN en el archivo .env "
                "(copia .env.example) o como variable de entorno."
            )
        self._token = token
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        # ``opener`` can be replaced in tests so no real network request is made.
        self._opener = opener or urllib.request.urlopen

    @staticmethod
    def encode_tag(tag: str) -> str:
        """Normalize a player tag and URL-encode the leading '#' (as '%23')."""
        cleaned = tag.strip().upper().lstrip("#")
        if not cleaned:
            raise ClashRoyaleError("El tag del jugador está vacío.")
        return "%23" + cleaned

    def _get(self, path: str) -> Any:
        url = f"{self._base_url}{path}"
        request = urllib.request.Request(
            url,
            headers={
                "Authorization": f"Bearer {self._token}",
                "Accept": "application/json",
            },
        )
        try:
            with self._opener(request, timeout=self._timeout) as response:
                body = response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            detail = ""
            try:
                data = json.loads(error.read().decode("utf-8"))
                detail = f" Detalle de la API: {data.get('reason', '')} {data.get('message', '')}".rstrip()
            except Exception:
                pass
            raise ClashRoyaleError(self._explain_http_error(error.code) + detail) from error
        except urllib.error.URLError as error:
            raise ClashRoyaleError(
                f"No se pudo conectar con la API ({error.reason}). Revisa tu conexión."
            ) from error

        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise ClashRoyaleError("La API devolvió una respuesta que no es JSON.") from error

    @staticmethod
    def _explain_http_error(status: int) -> str:
        if status in (401, 403):
            return (
                f"Acceso denegado ({status}). Revisa que la llave sea correcta y que la IP "
                "desde la que consultas esté permitida para esa llave en developer.clashroyale.com."
            )
        if status == 404:
            return "No se encontró el recurso (404). Revisa el tag del jugador."
        if status == 429:
            return "Demasiadas peticiones (429). Espera un momento e intenta de nuevo."
        if status >= 500:
            return f"Error del servidor de la API ({status}). Intenta más tarde."
        return f"La API respondió con el estado {status}."

    def get_cards(self) -> Any:
        """Return the full list of cards, exactly as the API sends it."""
        return self._get("/cards")

    def get_player(self, tag: str) -> Any:
        """Return a player's profile, exactly as the API sends it."""
        return self._get(f"/players/{self.encode_tag(tag)}")

    def get_battlelog(self, tag: str) -> Any:
        """Return a player's recent battles, exactly as the API sends it."""
        return self._get(f"/players/{self.encode_tag(tag)}/battlelog")
