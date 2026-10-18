"""Genera una página HTML con los mazos, para verlos en el navegador."""
import html
import json

from .cards import deck_profile
from .planner import plan_score
from .style import style_distance

ROLE_NAMES = {
    "win_condition": "Condición de victoria",
    "tank": "Tanque",
    "tank_killer": "Antitanque",
    "air_defense": "Defensa aérea",
    "support": "Apoyo",
    "swarm": "Enjambre",
    "building": "Edificio",
    "splash": "Daño en área",
    "spell_big": "Hechizo grande",
    "spell_small": "Hechizo pequeño",
    "spell_utility": "Hechizo de utilidad",
}


def load_icons(path="data/raw/cards.json"):
    """Devuelve {nombre: url de la imagen} a partir de cards.json."""
    with open(path, encoding="utf-8") as f:
        items = json.load(f)["items"]
    return {item["name"]: item.get("iconUrls", {}).get("medium") for item in items}


def card_html(name, cards, icons, es):
    """Una carta: imagen, costo y nombre en español."""
    cost = cards[name]["elixir"]
    url = icons.get(name)
    if url:
        picture = f'<img src="{html.escape(url)}" alt="{html.escape(es(name))}" loading="lazy">'
    else:
        picture = '<div class="no-img">Sin imagen</div>'
    return (
        '<div class="card">'
        f'{picture}<span class="cost">{cost if cost is not None else "?"}</span>'
        f'<span class="name">{html.escape(es(name))}</span>'
        "</div>"
    )


def deck_html(title, deck, cards, icons, es, base_profile, show_distance=True):
    """Un mazo: encabezado con sus números, las 8 cartas y sus roles."""
    profile = deck_profile(deck, cards)
    distance = style_distance(profile, base_profile)
    roles = "".join(
        f'<span class="chip">{ROLE_NAMES.get(role, role)} × {count}</span>'
        for role, count in sorted(profile["roles"].items(), key=lambda r: -r[1])
    )
    stats = f'Elixir {profile["avg_elixir"]:.2f}'
    if show_distance:
        stats += f" · Distancia al base {distance:.2f}"
    return (
        '<section class="deck">'
        f'<header><h3>{html.escape(title)}</h3><p>{stats}</p></header>'
        f'<div class="grid">{"".join(card_html(n, cards, icons, es) for n in deck)}</div>'
        f'<div class="chips">{roles}</div>'
        "</section>"
    )


def write_report(path, base, plans, cards, icons, es):
    """plans: lista de (título, [mazo temporada 2, ..., mazo temporada 5])."""
    base_profile = deck_profile(base, cards)
    parts = ['<h2>Temporada 1 (tu mazo)</h2>', deck_html("Mazo base", base, cards, icons, es, base_profile, show_distance=False)]
    for title, decks in plans:
        total = plan_score(decks, cards, base_profile)
        parts.append(f'<h2>{html.escape(title)} <small>distancia total {total:.2f}</small></h2>')
        for offset, deck in enumerate(decks):
            parts.append(deck_html(f"Temporada {offset + 2}", deck, cards, icons, es, base_profile))

    page = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Plan de mazos</title>
<style>
  body {{ margin: 0; padding: 24px 16px; background: #14213d; color: #f1f1f1;
         font-family: system-ui, sans-serif; }}
  main {{ max-width: 900px; margin: 0 auto; }}
  h1 {{ margin: 0 0 4px; }}
  h2 {{ margin: 40px 0 12px; border-bottom: 2px solid #f4c430; padding-bottom: 6px; }}
  h2 small {{ font-size: 0.6em; color: #f4c430; font-weight: normal; }}
  .deck {{ background: #1f2f57; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
  .deck header {{ display: flex; justify-content: space-between; align-items: baseline;
                  flex-wrap: wrap; gap: 8px; }}
  .deck h3 {{ margin: 0; }}
  .deck p {{ margin: 0; color: #c9d1e8; }}
  .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 14px 0; }}
  .card {{ position: relative; text-align: center; }}
  .card img, .no-img {{ width: 100%; aspect-ratio: 5 / 6; object-fit: contain; }}
  .no-img {{ display: flex; align-items: center; justify-content: center; background: #2c3e6e;
             border-radius: 8px; font-size: 0.8em; }}
  .cost {{ position: absolute; top: 2px; left: 2px; width: 26px; height: 26px; border-radius: 50%;
           background: #c33bd3; color: #fff; font-weight: bold; line-height: 26px; }}
  .name {{ display: block; font-size: 0.8em; margin-top: 4px; }}
  .chips {{ display: flex; flex-wrap: wrap; gap: 6px; }}
  .chip {{ background: #2c3e6e; border-radius: 999px; padding: 3px 10px; font-size: 0.8em; }}
</style>
</head>
<body>
<main>
<h1>Plan de mazos por temporada</h1>
<p>Sin repetir cartas entre temporadas. Menor distancia = más parecido a tu estilo.</p>
{"".join(parts)}
</main>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
