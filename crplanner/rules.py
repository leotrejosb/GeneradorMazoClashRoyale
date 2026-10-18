MAX_AVG_ELIXIR = 3.8
CHEAP_COST = 3            # una carta es "barata" si cuesta 3 o menos
MIN_CHEAP_CARDS = 3       # mínimo de cartas baratas en el mazo
FORBIDDEN_ROLES = {"spell_big", "spell_small"}
REQUIRED_ROLES = ["win_condition", "air_defense", "splash"]
FORBIDDEN_CARDS = {
    "Golem", "Sparky", "Three Musketeers", "Lava Hound",
    "Royal Recruits", "Elixir Collector", "Barbarian Hut",
}
HEAVY_COST = 6        # una carta es "pesada" si cuesta 6 o más
MAX_HEAVY_CARDS = 1   # máximo una pesada por mazo (ej. el Megacaballero)
def deck_problems(deck, cards):
    """Devuelve una lista con los problemas del mazo. Lista vacía = mazo válido."""
    problems = []
        # 1. Todos los nombres existen
    for name in deck:
        if name not in cards:
            raise ValueError(f"La carta '{name}' no existe en cards.json")

    # 2. Son 8 cartas distintas
    if len(deck) != 8 or len(set(deck)) != 8:
        problems.append("El mazo debe tener 8 cartas distintas")

    # 3. Lista de costos (si una carta no tiene costo, como Mirror, es un problema)
    costs = []
    for name in deck:
        elixir = cards[name]["elixir"]
        if elixir is None:
            problems.append(f"{name} no tiene costo fijo")
        else:
            costs.append(elixir)

    # 4. El promedio no puede pasar del máximo
    if costs and sum(costs) / len(costs) > MAX_AVG_ELIXIR:
        problems.append(f"Elixir promedio demasiado alto ({sum(costs) / len(costs):.2f})")
            
    # 6. Cartas baratas
    cheap_count = 0
    for cost in costs:
        if cost <= CHEAP_COST:
            cheap_count += 1
    if cheap_count < MIN_CHEAP_CARDS:
        problems.append("Faltan cartas baratas")

    # 7. Cartas prohibidas
    for name in deck:
        if name in FORBIDDEN_CARDS:
            problems.append(f"La carta {name} está prohibida")
    
    heavy_count = sum(1 for cost in costs if cost >= HEAVY_COST)
    if heavy_count > MAX_HEAVY_CARDS:
        problems.append(f"Demasiadas cartas pesadas ({heavy_count})")

    # 6. Roles
    roles = []
    for name in deck:
        roles.extend(cards[name]["roles"])

    for role in FORBIDDEN_ROLES:
        if role in roles:
            problems.append(f"Tiene un rol prohibido: {role}")
    for role in REQUIRED_ROLES:
        if role not in roles:
            problems.append(f"Falta el rol: {role}")

    return problems


