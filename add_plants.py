from database import init_db, add_plant
import sqlite3

init_db()

# DELETE ALL OLD PLANTS
conn = sqlite3.connect("plants.db")
conn.execute("DELETE FROM plants")
conn.commit()
conn.close()
print("✓ Cleared old plants\n")

plants = [
    ("Star Jasmine", "Trachelospermum jasminoides", 5),
    ("Cats Pajamas", "Tradescantia pallida", 4),
    ("Denim n Lace", "Tradescantia zebrina", 4),
    ("Catsmeow", "Tradescantia fluminensis", 4),
    ("Basil", "Ocimum basilicum", 3),
    ("Ghost Pepper", "Capsicum chinense", 4),
    ("Jalapeno", "Capsicum annuum", 4),
    ("Hungarian Wax Pepper", "Capsicum annuum", 4),
    ("Oregano", "Origanum vulgare", 5),
    ("Lemon Thyme", "Thymus citriodorus", 5),
    ("Rosemary", "Rosmarinus officinalis", 6),
    ("Spring Onion", "Allium fistulosum", 3),
    ("Strawberry", "Fragaria x ananassa", 4),
    ("Fig Tree", "Ficus carica", 7),
    ("Cucumber", "Cucumis sativus", 3),
    ("Zucchini", "Cucurbita pepo", 3),
    ("Squash", "Cucurbita maxima", 3),
    ("Lavender", "Lavandula angustifolia", 6),
    ("Tomato", "Solanum lycopersicum", 3),
    ("Strawberry Mojito Mint", "Mentha spicata", 3),
    ("Dill", "Anethum graveolens", 4),
    ("Shishito Pepper", "Capsicum annuum", 4),
    ("Lettuce", "Lactuca sativa", 3),
]

plant_counts = {
    "Star Jasmine": 2,
    "Cats Pajamas": 2,
    "Catsmeow": 2,
    "Basil": 2,
    "Ghost Pepper": 3,
    "Spring Onion": 2,
    "Strawberry": 2,
    "Tomato": 2,
    "Strawberry Mojito Mint": 1,
    "Dill": 2,
    "Lettuce": 2,
}

for name, species, freq in plants:
    count = plant_counts.get(name, 1)
    for i in range(count):
        suffix = f" #{i+1}" if count > 1 else ""
        add_plant(f"{name}{suffix}", species, freq)
        print(f"✓ Added {name}{suffix}")

print(f"\n✓ All plants added!")