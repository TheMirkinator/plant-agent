import sqlite3
from datetime import datetime

DB_PATH = "plants.db"

def init_db():
    """Create the database and tables."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS plants (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE NOT NULL,
        species TEXT,
        last_watered TEXT,
        water_freq_days INTEGER DEFAULT 7,
        notes TEXT
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS health_logs (
        id INTEGER PRIMARY KEY,
        plant_id INTEGER,
        timestamp TEXT,
        observation TEXT,
        FOREIGN KEY (plant_id) REFERENCES plants(id)
    )""")
    conn.commit()
    conn.close()

def add_plant(name, species, water_freq_days=7):
    """Add a new plant to the database."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute("""INSERT INTO plants (name, species, water_freq_days, last_watered)
                       VALUES (?, ?, ?, ?)""",
                    (name, species, water_freq_days, datetime.now().isoformat()))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_all_plants():
    """Get all plants as list of dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    plants = conn.execute("SELECT * FROM plants").fetchall()
    conn.close()
    return [dict(p) for p in plants]

def get_plants_needing_water():
    """Get plants that are overdue for watering."""
    from datetime import datetime, timedelta
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    plants = conn.execute("SELECT * FROM plants").fetchall()
    conn.close()
    
    overdue = []
    for plant in plants:
        last_watered = datetime.fromisoformat(plant['last_watered'])
        days_since = (datetime.now() - last_watered).days
        if days_since >= plant['water_freq_days']:
            overdue.append({
                'name': plant['name'],
                'days_overdue': days_since - plant['water_freq_days']
            })
    return overdue

def update_water_date(plant_name):
    """Record that a plant was just watered."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE plants SET last_watered = ? WHERE name = ?",
                (datetime.now().isoformat(), plant_name))
    conn.commit()
    conn.close()

def log_observation(plant_name, observation):
    """Log a health observation."""
    conn = sqlite3.connect(DB_PATH)
    plant = conn.execute("SELECT id FROM plants WHERE name = ?", (plant_name,)).fetchone()
    if plant:
        conn.execute("""INSERT INTO health_logs (plant_id, timestamp, observation)
                       VALUES (?, ?, ?)""",
                    (plant[0], datetime.now().isoformat(), observation))
        conn.commit()
    conn.close()

def build_plant_context():
    """Return plant data formatted for Claude's system prompt."""
    plants = get_all_plants()
    if not plants:
        return "No plants in database yet."
    
    lines = []
    for p in plants:
        last = p['last_watered'][:10] if p['last_watered'] else "never"
        lines.append(f"- {p['name']} ({p['species']}): last watered {last}, every {p['water_freq_days']} days")
    return "Your plants:\n" + "\n".join(lines)