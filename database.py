import sqlite3
from datetime import datetime
from venv import logger
from requests import Session
from logging_setup import logger
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from logging_setup import logger

engine = create_engine("sqlite:///plants.db")
engine = create_engine("sqlite:///plants.db")
DB_PATH = "plants.db"

def init_db():
    """Initialize all database tables."""
    with engine.begin() as conn:
        # Existing tables (keep these)
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS plants (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                scientific_name TEXT,
                watering_frequency_days INTEGER,
                last_watered DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS health_logs (
                id INTEGER PRIMARY KEY,
                plant_id INTEGER,
                observation TEXT,
                logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(plant_id) REFERENCES plants(id)
            )
        """))
        
        # NEW: Conversations table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                role TEXT,
                message TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
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

def store_conversation(chat_id, role, message):
    """Store a message in conversation history."""
    with Session(engine) as session:
        try:
            session.execute(text("""
                INSERT INTO conversations (chat_id, role, message)
                VALUES (:chat_id, :role, :message)
            """), {
                "chat_id": chat_id,
                "role": role,
                "message": message
            })
            session.commit()
            logger.info(f"Conversation stored for chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to store conversation: {e}")

def get_recent_conversations(chat_id, limit=5):
    """Get last N messages from conversation history."""
    with Session(engine) as session:
        try:
            result = session.execute(text("""
                SELECT role, message FROM conversations
                WHERE chat_id = :chat_id
                ORDER BY timestamp DESC
                LIMIT :limit
            """), {
                "chat_id": chat_id,
                "limit": limit
            }).fetchall()
            
            # Reverse to get chronological order
            messages = [{"role": row[0], "content": row[1]} for row in reversed(result)]
            return messages
        except Exception as e:
            logger.error(f"Failed to get conversations: {e}")
            return []