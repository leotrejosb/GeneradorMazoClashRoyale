
import json
import os
from collections import Counter

RAW = os.path.join("data", "raw")


def load(name):
    with open(os.path.join(RAW, name), encoding="utf-8") as handle:
        return json.load(handle)


cards = load("cards.json")
items = cards["items"]
print(f"Cartas: {len(items)}")
print("Rarezas:", dict(Counter(card["rarity"] for card in items)))

with_evolution = [card["name"] for card in items if card.get("maxEvolutionLevel")]
print(f"Cartas con evolución ({len(with_evolution)}):", ", ".join(with_evolution))
print("Ejemplo:", items[0]["name"], "| elixir:", items[0].get("elixirCost"))
print("supportItems:", [card["name"] for card in cards.get("supportItems", [])])

print()
battles = load("battlelog.json")
print(f"Batallas: {len(battles)}")
modes = Counter((b.get("type"), b.get("gameMode", {}).get("name")) for b in battles)
for (kind, mode), count in modes.most_common():
    print(f"  {count} x tipo={kind} | modo={mode}")

print()
print("Mazo usado en las 5 batallas más recientes:")
for battle in battles[:5]:
    deck = [card["name"] for card in battle["team"][0].get("cards", [])]
    print(battle["battleTime"], "|", battle.get("gameMode", {}).get("name"), "|", ", ".join(deck))