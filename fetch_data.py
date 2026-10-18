"""Download cards, player profile and battle log from the official Clash Royale API.

Usage:
    python fetch_data.py --tag "#YOURTAG"

The raw responses are saved under data/raw/ so the rest of the project can work offline.
"""

from __future__ import annotations

import argparse
import json
import os
import sys

from crplanner import ClashRoyaleClient, ClashRoyaleError, load_env_file


def save_json(payload, path: str) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def describe(payload, label: str) -> None:
    """Print a short, token-free summary so you can see what the API actually returned."""
    if isinstance(payload, dict):
        print(f"- {label}: claves de nivel superior -> {', '.join(sorted(payload.keys()))}")
        items = payload.get("items")
        if isinstance(items, list) and items:
            print(f"  {len(items)} elementos en 'items'. Campos del primero: {', '.join(sorted(items[0].keys()))}")
    elif isinstance(payload, list):
        print(f"- {label}: lista con {len(payload)} elementos")
        if payload and isinstance(payload[0], dict):
            print(f"  Campos del primero: {', '.join(sorted(payload[0].keys()))}")
    else:
        print(f"- {label}: {type(payload).__name__}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Descarga datos de la API de Clash Royale.")
    parser.add_argument("--tag", help="Tag del jugador, por ejemplo #ABC123 (o define CR_PLAYER_TAG)")
    parser.add_argument("--out", default=os.path.join("data", "raw"), help="Carpeta de salida")
    args = parser.parse_args()

    load_env_file(".env")
    tag = args.tag or os.environ.get("CR_PLAYER_TAG", "")

    os.makedirs(args.out, exist_ok=True)

    try:
        client = ClashRoyaleClient(os.environ.get("CR_API_TOKEN", ""))

        print("Descargando cartas...")
        cards = client.get_cards()
        save_json(cards, os.path.join(args.out, "cards.json"))
        describe(cards, "cards")

        if tag:
            print("Descargando perfil...")
            player = client.get_player(tag)
            save_json(player, os.path.join(args.out, "player.json"))
            describe(player, "player")

            print("Descargando registro de batallas...")
            battles = client.get_battlelog(tag)
            save_json(battles, os.path.join(args.out, "battlelog.json"))
            describe(battles, "battlelog")
        else:
            print("Sin tag de jugador: solo se descargaron las cartas.")
    except ClashRoyaleError as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(f"Listo. Archivos guardados en {args.out}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
