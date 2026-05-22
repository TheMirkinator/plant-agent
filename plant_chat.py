import os
from anthropic import Anthropic
from dotenv import load_dotenv
from logging_setup import setup_logging, logger
from database import init_db, build_plant_context
from tools import TOOLS, execute_tool
from scheduler import start_scheduler
from telegram_notifications import send_telegram_message
from prompts import PLANT_CARE_SYSTEM, USER_CONFIG


load_dotenv()
setup_logging()
init_db()  # Initialize database on startup
client = Anthropic()

# System prompt is now in prompts.py

def chat():
    messages = []
    # Start the background scheduler
    scheduler = start_scheduler()
    print("🌿 Plant Assistant — type 'quit' to exit\n")
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit", ""):
            break

        messages.append({"role": "user", "content": user_input})
        logger.info(f"User: {user_input}")

        try:
            # Build system prompt
            plant_context = build_plant_context()
            system_prompt = PLANT_CARE_SYSTEM.format(
                plant_context=plant_context,
                **USER_CONFIG
            )
            
            # Agent loop: keep going until Claude gives a final answer
            max_iterations = 10
            iterations = 0
            
            while iterations < max_iterations:
                iterations += 1
                logger.info(f"Agent iteration {iterations}")
                
                # Call Claude with tools available
                response = client.messages.create(
                    model="claude-haiku-4-5",
                    max_tokens=2048,
                    system=system_prompt,
                    tools=TOOLS,
                    messages=messages
                )
                
                # Check if Claude wants to use a tool
                if response.stop_reason == "tool_use":
                    # Find the tool_use block in the response
                    tool_use_block = None
                    for block in response.content:
                        if block.type == "tool_use":
                            tool_use_block = block
                            break
                    
                    if tool_use_block:
                        tool_name = tool_use_block.name
                        tool_input = tool_use_block.input
                        tool_use_id = tool_use_block.id
                        
                        logger.info(f"Claude called tool: {tool_name} with input: {tool_input}")
                        
                        # Execute the tool
                        tool_result = execute_tool(tool_name, tool_input)
                        logger.info(f"Tool result: {tool_result}")
                        
                        # Add Claude's response (with tool_use) to messages
                        messages.append({"role": "assistant", "content": response.content})
                        
                        # Add the tool result back to messages
                        messages.append({
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": tool_use_id,
                                    "content": tool_result
                                }
                            ]
                        })
                        
                        # Loop continues — Claude will see the tool result and respond
                
                elif response.stop_reason == "end_turn":
                    # Claude is done — get the final response
                    final_response = ""
                    for block in response.content:
                        if hasattr(block, "text"):
                            final_response = block.text
                            break
                    
                    # Add to message history
                    messages.append({"role": "assistant", "content": final_response})
                    logger.info(f"Claude final response: {final_response[:100]}...")
                    
                    # Print response to user
                    print(f"\n🌿 {final_response}\n")
                    break
                
                else:
                    logger.warning(f"Unexpected stop_reason: {response.stop_reason}")
                    break

        except Exception as e:
            logger.error(f"API error: {e}")
            print(f"Something went wrong: {e}")

if __name__ == "__main__":
    chat()