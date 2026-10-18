"""Agrega el rol 'splash' (daño en área, sirve contra ejércitos) a roles.csv."""
import csv

SPLASH = [
    "Valkyrie", "Ice Wizard", "Princess", "Bomber", "Wizard", "Baby Dragon",
    "Witch", "Executioner", "Bowler", "Dark Prince", "Mega Knight",
    "Firecracker", "Skeleton Dragons", "Bomb Tower", "Electro Dragon",
    "Royal Ghost", "Sparky", "Fire Spirit", "Goblin Demolisher",
    "Skeleton King", "Hunter",
]

with open("data/roles.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fields = reader.fieldnames
    rows = list(reader)

names = {row["name"] for row in rows}
print("No encontradas:", [n for n in SPLASH if n not in names])

for row in rows:
    roles = row["roles"].split(";")
    if row["name"] in SPLASH and "splash" not in roles:
        roles.append("splash")
        row["roles"] = ";".join(roles)

with open("data/roles.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)