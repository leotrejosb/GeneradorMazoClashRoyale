import random

from .cards import deck_profile
from .rules import deck_problems
from .style import style_distance


def best_deck(base_profile, pool, cards, tries=20000):
    """Prueba mazos al azar y devuelve el válido más parecido al perfil base."""
    best = None
    best_distance = None
    for _ in range(tries):
        deck = random.sample(pool, 8)       # 8 cartas distintas al azar
        if deck_problems(deck, cards):      # si tiene problemas, lo saltamos
            continue
        distance = style_distance(deck_profile(deck, cards), base_profile)
        if best is None or distance < best_distance:
            best = deck
            best_distance = distance
    if best is None:
        raise ValueError("No se encontró ningún mazo válido")
    return best, best_distance


def plan_seasons(base_deck, cards, seasons=4, tries=20000):
    """Arma un mazo por temporada, sin repetir cartas entre temporadas."""
    base_profile = deck_profile(base_deck, cards)
    pool = [name for name in cards if name not in base_deck]
    plan = []
    for _ in range(seasons):
        deck, distance = best_deck(base_profile, pool, cards, tries)
        if deck is None:
            raise ValueError("No se encontró ningún mazo válido")
        plan.append((deck, distance))
        pool = [name for name in pool if name not in deck]   # quita las cartas usadas
    return plan


def plan_score(decks, cards, base_profile):
    """Qué tan lejos está un plan del estilo base: suma de las distancias de sus mazos."""
    total = 0
    for deck in decks:
        if deck_problems(deck, cards):
            return float('inf')
        total += style_distance(deck_profile(deck, cards), base_profile)
    return total


def swap(list_a, i, list_b, j):
    """Intercambia list_a[i] con list_b[j]."""
    list_a[i], list_b[j] = list_b[j], list_a[i]


def improve_plan(decks, cards, base_deck, iterations=100000):
    """Mejora un plan cambiando cartas de a una, sin romper las reglas."""
    base_profile = deck_profile(base_deck, cards)
    decks = [list(deck) for deck in decks]
    used = set(base_deck) | {name for deck in decks for name in deck}
    unused = [name for name in cards if name not in used]
    current = plan_score(decks, cards, base_profile)

    for _ in range(iterations):
        i = random.randrange(len(decks))      # mazo elegido
        p = random.randrange(8)               # posición de la carta dentro del mazo
        if random.random() < 0.5:             # la mitad de las veces: cambiar por una carta libre
            other_list, q = unused, random.randrange(len(unused))
        else:                                 # la otra mitad: cambiar con una carta de otro mazo
            j = random.choice([x for x in range(len(decks)) if x != i])
            other_list, q = decks[j], random.randrange(8)

        swap(decks[i], p, other_list, q)      # hacemos el cambio
        if deck_problems(decks[i], cards):
            swap(decks[i], p, other_list, q)
            continue
        new_score = plan_score(decks, cards, base_profile)
        if new_score <= current:
            current = new_score
        else:
            swap(decks[i], p, other_list, q)
    return decks