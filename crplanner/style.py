ELIXIR_WEIGHT = 1   # cuánto pesa la diferencia de elixir (esto lo decides tú)
SPREAD_WEIGHT = 2

def style_distance(profile_a, profile_b):
    """Qué tan distintos son dos perfiles. 0 = idénticos; menor = más parecidos."""
    elixir_distance = abs(profile_a["avg_elixir"] - profile_b["avg_elixir"]) * ELIXIR_WEIGHT
    spread_distance = abs(profile_a["cost_spread"] - profile_b["cost_spread"]) * SPREAD_WEIGHT
    roles_distance = 0
    for role in set(profile_a["roles"]) | set(profile_b["roles"]):
        roles_distance += abs(profile_a["roles"].get(role, 0) - profile_b["roles"].get(role, 0))
    return elixir_distance + roles_distance + spread_distance

