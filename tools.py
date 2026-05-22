from database import (
    get_all_plants, 
    get_plants_needing_water, 
    update_water_date, 
    log_observation,
    add_plant
)
from logging_setup import logger

# Define tools for Claude to use
TOOLS = [
    {
        "name": "get_plants_needing_water",
        "description": "Get a list of plants that are overdue for watering based on their schedule. Use this when the user asks which plants need water.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "update_water_date",
        "description": "Record that a plant has just been watered. Call this when the user says they watered a plant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plant_name": {
                    "type": "string",
                    "description": "The name of the plant that was watered"
                }
            },
            "required": ["plant_name"]
        }
    },
    {
        "name": "log_plant_observation",
        "description": "Log a health observation about a plant (e.g., yellow leaves, new growth, pest damage). Call this when the user describes what their plant looks like.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plant_name": {
                    "type": "string",
                    "description": "The name of the plant"
                },
                "observation": {
                    "type": "string",
                    "description": "What the user observed about the plant's health or appearance"
                }
            },
            "required": ["plant_name", "observation"]
        }
    },
    {
        "name": "add_plant",
        "description": "Add a new plant to the user's collection. Call this when they say they got a new plant.",
        "input_schema": {
            "type": "object",
            "properties": {
                "plant_name": {
                    "type": "string",
                    "description": "Common name of the plant"
                },
                "species": {
                    "type": "string",
                    "description": "Scientific name or species of the plant"
                },
                "water_freq_days": {
                    "type": "integer",
                    "description": "How many days between waterings (default: 7)"
                }
            },
            "required": ["plant_name", "species"]
        }
    },
    {
        "name": "get_all_plants",
        "description": "Get a list of all plants the user is currently growing.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }
]

def execute_tool(tool_name, tool_input):
    """Execute a tool and return the result."""
    logger.info(f"Executing tool: {tool_name} with input: {tool_input}")
    
    try:
        if tool_name == "get_plants_needing_water":
            plants = get_plants_needing_water()
            if not plants:
                return "No plants need watering right now!"
            result = "Plants needing water:\n"
            for plant in plants:
                result += f"- {plant['name']} ({plant['days_overdue']} days overdue)\n"
            return result
        
        elif tool_name == "update_water_date":
            plant_name = tool_input.get("plant_name")
            update_water_date(plant_name)
            return f"✓ Recorded that {plant_name} was watered today!"
        
        elif tool_name == "log_plant_observation":
            plant_name = tool_input.get("plant_name")
            observation = tool_input.get("observation")
            log_observation(plant_name, observation)
            return f"✓ Logged observation for {plant_name}: {observation}"
        
        elif tool_name == "add_plant":
            plant_name = tool_input.get("plant_name")
            species = tool_input.get("species")
            water_freq = tool_input.get("water_freq_days", 7)
            success = add_plant(plant_name, species, water_freq)
            if success:
                return f"✓ Added {plant_name} to your collection!"
            else:
                return f"Error: {plant_name} already exists in your collection."
        
        elif tool_name == "get_all_plants":
            plants = get_all_plants()
            if not plants:
                return "You don't have any plants yet!"
            result = "Your plants:\n"
            for plant in plants:
                last_watered = plant['last_watered'][:10] if plant['last_watered'] else "never"
                result += f"- {plant['name']} ({plant['species']}): last watered {last_watered}, every {plant['water_freq_days']} days\n"
            return result
        
        else:
            return f"Unknown tool: {tool_name}"
    
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return f"Error executing {tool_name}: {e}"