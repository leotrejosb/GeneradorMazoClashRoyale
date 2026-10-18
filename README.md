# Clash Royale Season Planner

Builds Clash Royale decks for seasons 2–5 from the deck I played in season 1, **without repeating a single card across seasons** and keeping my play style.

> Demo video: _[Loom link]_

![Deck plan report](docs/plan.png)

## The problem

I play a personal Clash Royale challenge with five seasons. In season 1 I can pick any 8 cards. From then on, **a card used in any previous season can never be used again**. All cards sit at level 15–16, so card level is not a factor: the only question is *which* cards to pick.

That means 40 different cards over five seasons. The hard part is not finding one good deck, it is splitting the good cards across four decks so that the last season is not left with whatever remains.

My season 1 deck, which defines my style:

> Mini P.E.K.K.A, Valkyrie, Musketeer, Hog Rider, Goblin Barrel, Ice Wizard, Princess, Skeleton Army
> Average elixir 3.5 · every card costs 3 or 4 · fast transitions, no damage spells, no heavy cards

## How it works

```
cards.json (official API) ──┐
roles.csv (hand-labeled) ───┼─> card data ─> deck profile ─> distance to my style
seasons.json (my deck) ─────┘                                      │
                                     validity rules ───────────────┤
                                                                   v
                              simple method  vs  planned method ─> plan.html
```

### 1. Data

- **Card list** from the [official Clash Royale API](https://developer.clashroyale.com) (`/cards`): 123 cards with elixir cost and image.
- **Card roles** are not in the API, so I labeled them in `data/roles.csv`: `win_condition`, `tank`, `tank_killer`, `air_defense`, `support`, `swarm`, `building`, `splash`, `spell_big`, `spell_small`, `spell_utility`. A card can have several roles.
- **Spanish names** in `data/names_es.csv`, used only for display. Internally the program uses the API names.

### 2. Deck profile and style distance

A deck is summarized as:

- average elixir,
- how many cards it has of each role,
- **cost spread** (standard deviation of card costs).

The distance between two decks is:

```
|Δ avg elixir| × 1  +  Σ |Δ cards per role|  +  |Δ cost spread| × 2
```

Lower means closer to my style; 0 means the same profile.

### 3. Validity rules

A deck is only considered if it passes every rule (`crplanner/rules.py`). Each rule comes from how I play or from a real game where a generated deck failed:

| Rule | Why |
|---|---|
| 8 different cards | Game rule. |
| Average elixir ≤ 3.8 | I play fast transitions: counter-attack while the opponent is out of elixir. |
| At least 3 cards costing ≤ 3 | Cheap cards make the deck cycle fast. |
| No damage spells (Fireball, Arrows, Log…) | I don't play them. |
| At least one win condition and one air defense | Minimum for a playable deck. |
| **At least one splash card** | Added after testing: a generated deck had nothing to stop a Skeleton Army or Goblin Gang. My season 1 deck had Valkyrie for that. |
| **Banned cards** (Golem, Sparky, Three Musketeers, Lava Hound…) | Added after testing: slow or fragile expensive cards that don't fit fast transitions. Expensive but sturdy cards like Mega Knight are still allowed. |
| At most one card costing ≥ 6 | Two of them leave no room for cheap cards under the 3.8 average. |

### 4. Two ways to build the plan

**Simple method (greedy).** For each season in order, try 20,000 random valid decks from the remaining cards and keep the closest to my style. Then remove its cards and move to the next season.
Weakness: early seasons take the best cards and the last season gets the leftovers.

**Planned method (local search).** Start from the simple plan and try 100,000 small changes: swap a card with an unused card, or with a card from another season's deck. Undo any change that breaks a rule or makes the total distance worse. Because cards can move *between* seasons, the good cards get shared instead of being used up early.

## Results

One run (`random.seed(7)`, all current rules):

| | Simple | Planned |
|---|---|---|
| Total distance (4 decks) | 16.45 | **6.20** |
| Worst season | 5.03 (season 5) | 3.03 |

The planned method cuts the total distance by 62%. In the simple method the distance grows season by season, which is the leftovers problem it was built to show. Earlier runs with other seeds and earlier versions of the rules showed the same pattern.

### What I learned along the way

- **A metric that is too easy to satisfy is a bug.** The first version only used average elixir and roles, and the planned method reached a distance of 0.00 in all four seasons, mixing 1-elixir and 6-elixir cards to hit the same average. Adding cost spread fixed it.
- **Testing in the real game found what the numbers missed.** A season 2 deck with Sparky looked fine by the metric but lost to swarms. That game produced the splash and banned-card rules. With the new rules I played noticeably better, though over too few games to call it a measured result.

## How to run

Requires Python 3.10+. `main.py` uses only the standard library.

```bash
git clone https://github.com/leotrejosb/GeneradorMazoClashRoyale.git
cd GeneradorMazoClashRoyale
python main.py
```

It prints both plans in the terminal and opens `plan.html` in the browser with every deck, card images, elixir, distance and roles.

To use your own season 1 deck, edit `data/seasons.json` with the API card names.

### Refreshing the card list (optional)

`data/raw/cards.json` is already included. To download it again you need a free token from the [Clash Royale developer site](https://developer.clashroyale.com):

1. Copy `.env.example` to `.env` and put your token there. `.env` is git-ignored.
2. Run `python fetch_data.py`.

## Project structure

```
crplanner/
  client.py    API client
  cards.py     loads cards + roles, builds the deck profile
  style.py     distance between profiles
  rules.py     validity rules
  planner.py   simple and planned methods
  report.py    HTML report
data/
  raw/cards.json   card list from the API
  roles.csv        hand-labeled roles
  names_es.csv     Spanish names
  seasons.json     season 1 deck
tests/             tests for the rules and the no-repeat constraint
main.py            runs everything
fetch_data.py      downloads data from the API
add_splash.py      one-off script that added the splash role
```

## Limitations

- **Roles are my labels, not official data.** Some newer cards (Goblinstein, Rune Giant, Boss Bandit…) are labeled with less confidence. The results are only as good as `roles.csv`.
- **The distance is a design decision.** The weights (1 for elixir, 2 for cost spread) were chosen by testing, not derived. "Close to my style" means "similar numbers", not "plays the same".
- **It doesn't know the meta or matchups.** It proposes coherent decks for my style; it doesn't promise they win.
- **Local search can get stuck** in a good but not optimal plan. Running it several times and keeping the best result would help.

## Next steps

- Run many seeds and report averages instead of a single run.
- Restarts or simulated annealing for the planned method.
- A per-deck usage guide, left out because I couldn't validate it with data.

## Use of AI

I built this with Claude as a pair: it proposed approaches and explained concepts, and I wrote and tested the core functions (deck profile, distance, rules, planner) and made the design decisions. The rules come from my own games.