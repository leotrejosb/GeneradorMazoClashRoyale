
import json
import random
import csv
from crplanner.cards import load_cards, deck_profile
from crplanner.planner import plan_seasons, plan_score, improve_plan
from crplanner.style import style_distance
import os
import webbrowser

from crplanner.report import load_icons, write_report

def load_spanish_names(path="data/names_es.csv"):
    """Devuelve {nombre_en_ingles: nombre_en_español}."""
    with open(path, encoding="utf-8") as f:
        return {row["name"]: row["nombre_es"] for row in csv.DictReader(f)}


SPANISH = load_spanish_names()


def es(name):
    """Traduce un nombre; si no está en el archivo, lo deja en inglés."""
    return SPANISH.get(name, name)


def show_plan(title, decks, cards, base_profile, first_season=2):
    print(f"\n{title}")
    for offset, deck in enumerate(decks):
        profile = deck_profile(deck, cards)
        distance = style_distance(profile, base_profile)
        print(f"  Temporada {first_season + offset}: {', '.join(es(n) for n in deck)}")
        print(f"     elixir {profile['avg_elixir']:.2f} | distancia al base {distance:.2f}")
    print(f"  Distancia total: {plan_score(decks, cards, base_profile):.2f}")


def main():
    random.seed(7)   # para que la demo salga igual cada vez; quítalo para ver mazos distintos
    cards = load_cards()
    with open("data/seasons.json", encoding="utf-8") as f:
        base = json.load(f)["season_1"]
    base_profile = deck_profile(base, cards)

    print("Mazo base (temporada 1):", ", ".join(es(n) for n in base))
    print(f"  elixir {base_profile['avg_elixir']:.2f} | roles {base_profile['roles']}")

    simple = [deck for deck, _ in plan_seasons(base, cards)]
    show_plan("Método simple (una temporada tras otra)", simple, cards, base_profile)

    planned = improve_plan(simple, cards, base)
    show_plan("Método planificado (las 4 temporadas juntas)", planned, cards, base_profile)

    icons = load_icons()
    plans = [("Método simple", simple), ("Método planificado", planned)]
    write_report("plan.html", base, plans, cards, icons, es)
    print("\nPágina generada: plan.html")
    webbrowser.open("file://" + os.path.abspath("plan.html"))


if __name__ == "__main__":
    main()