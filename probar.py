import json
from crplanner.cards import load_cards
from collections import Counter
cartas = load_cards()
mazo = json.load(open("data/seasons.json", encoding="utf-8"))["season_1"]

costos = []
conteo = Counter()
for nombre in mazo:
    carta = cartas[nombre]
    for rol in carta["roles"]:
        conteo[rol] += 1

print(dict(conteo))