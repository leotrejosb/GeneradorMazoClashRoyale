"""Carga y unión de los datos de cartas."""
import csv
import json
from collections import Counter
import statistics
def load_cards(cards_path="data/raw/cards.json", roles_path="data/roles.csv"):
    """Devuelve un diccionario {nombre: carta} con elixir, rareza y roles."""
    with open(cards_path, encoding="utf-8") as f:
        items = json.load(f)["items"]

    with open(roles_path, encoding="utf-8") as f:
        roles_by_name = {row["name"]: row["roles"].split(";") for row in csv.DictReader(f)}

    cards = {}
    for item in items:
        name = item["name"]
        if name not in roles_by_name:
            raise ValueError(f"La carta '{name}' no está en roles.csv")
        cards[name] = {
            "name": name,
            "elixir": item.get("elixirCost"),  # Mirror no trae costo
            "rarity": item["rarity"],
            "roles": roles_by_name[name],
        }

    extra = set(roles_by_name) - set(cards)
    if extra:
        raise ValueError(f"Hay cartas en roles.csv que no están en cards.json: {sorted(extra)}")
    return cards

def deck_profile(deck, cards):
    """Devuelve el elixir promedio y cuántas cartas hay de cada rol en un mazo."""
    costos = []
    conteo = Counter()
    for nombre in deck:
        if nombre not in cards:
            raise ValueError(f"La carta '{nombre}' no existe en cards.json")
        carta = cards[nombre]
        if carta["elixir"] is not None:
            costos.append(carta["elixir"])
        for rol in carta["roles"]:
            conteo[rol] += 1
    return {"avg_elixir": sum(costos) / len(costos), "roles": dict(conteo), "cost_spread": statistics.pstdev(costos)}