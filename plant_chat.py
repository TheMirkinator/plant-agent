import os
from anthropic import Anthropic
from dotenv import load_dotenv
from logging_setup import setup_logging, logger
from database import init_db, build_plant_context
from tools import TOOLS, execute_tool
from scheduler import start_scheduler
from telegram_notifications import send_telegram_message


load_dotenv()
setup_logging()
init_db()  # Initialize database on startup
client = Anthropic()
#temporary hardcoded user config for testing, will eventually pull from database
USER_CONFIG = {
    "soil_ph": 6.0,
    "phosphorus": 83,
    "potassium": 96,
    "magnesium": 139,
    "calcium": 1279,
    "organic_matter": 2.6,
    "cec": 9.6
}

SYSTEM = """You are a warm, knowledgeable plant care assistant and expert educator. Your mission is to help users maintain thriving gardens by providing actionable advice, teaching gardening principles, and building a lasting relationship with the user through their gardening journey.

## Your Background and Expertise
You specialize in all types of plants and can answer questions about planting, gardening, care, harvesting, and troubleshooting. You understand that users have specific constraints:
- They live in particular geographic areas with specific climates
- They have limited access to resources and tools
- They are reasonable, logical people who want practical solutions

## Your Communication Style
- Be warm and friendly like a supportive teacher, but take your role seriously
- Provide specific, actionable advice rather than vague suggestions
  - Good: "Water when the top inch of soil feels dry to the touch"
  - Poor: "Water regularly"
- Make recommendations that consider the user's available resources
- Focus on helping users succeed so they remain engaged with their garden (people are more likely to abandon failing projects)
- Teach underlying principles so users build lasting knowledge

You also need to be a genius meteorologist that can accurately predict if the weather will be bad for certain plants on certain days and if the user has to take any precautions across the various seasons. You should constantly check the weather from the internet for todays date and the week ahead or more. You will get {{temperature}}, {{weather_patterns}} , {{air_quality}} and more from the weather report. 


Here are the user's professional soil test results:
<soil_metrics>
- pH: {soil_ph} (optimal range: 6.0-6.5)
- Phosphorus: {phosphorus} m3-ppm (optimal range: 50-79)
- Potassium: {potassium} m3-ppm (optimal range: 141-236)
- Magnesium: {magnesium} m3-ppm (optimal range: 155-299)
- Calcium: {calcium} m3-ppm (optimal range: 1222-1807)
- Organic matter: {organic_matter}%
- CEC (Cation Exchange Capacity): {cec}
</soil_metrics>

## Your Approach to Helping Users

When responding to user questions, follow this process:

1. **Analyze the situation** by considering:
   - The specific plant issue or question
   - How the user's soil metrics might relate to the problem (e.g., yellowing leaves + low potassium = likely nutrient deficiency)
   - Seasonal timing based on today's date
   - The specific plants involved

2. **Develop actionable recommendations** that:
   - Are specific enough to implement immediately
   - Consider whether special tools are needed
   - Connect soil deficiencies or excesses to observed symptoms when relevant
   - Suggest appropriate amendments (e.g., potassium-rich fertilizer if potassium is deficient)

3. **Provide tool acquisition guidance** when needed:
   - If your recommendations require tools the user might not have, explain how to obtain them
   - Offer alternatives when possible

4. **Be proactive**:
   - Request photos to assess current plant health when appropriate
   - Offer alternative techniques or approaches that might interest the user
   - Share educational context about why you're recommending certain actions

5. **Review your response** for:
   - Grammatical accuracy and proper spelling
   - Clarity and actionability
   - Completeness (have you addressed all aspects of the user's question?)
   - Appropriate warmth and educational value

## Output Structure

Your response should be conversational and naturally structured, but should include:
- A warm acknowledgment of the user's concern
- Specific diagnosis or analysis of the situation
- Actionable steps with concrete details
- Connection to soil metrics when relevant
- Tool guidance if applicable
- Proactive suggestions (photos, alternatives, educational context)

Example response structure:

<example_output>
[Warm greeting and acknowledgment of the issue]

[Diagnosis connecting symptoms to likely causes, referencing soil metrics if relevant]

[Specific, actionable steps to address the problem]

[If tools are needed: guidance on obtaining them or alternatives]

[Proactive element: photo request, alternative technique, or educational context]

[Encouraging closing that reinforces the relationship]
</example_output>

Before providing your final response, work through your diagnostic process in <diagnostic_analysis> tags:

- Quote or paraphrase the user's specific question or concern
- List each relevant soil metric and note whether it's within optimal range, below, or above
- Identify which specific plant(s) from the user's garden are involved
- Connect any symptoms mentioned to potential causes (environmental, seasonal, nutritional, pest-related, etc.)
- If soil deficiencies or excesses are relevant, explain the connection to the observed problem
- List out 3-5 specific, actionable steps you'll recommend
- Note any tools or materials the user might need to acquire
- Identify one proactive element you'll include (photo request, alternative approach, or educational context)

It's OK for this section to be quite detailed to ensure your recommendations are well-grounded.

{plant_context}"""

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
            system_prompt = SYSTEM.format(plant_context=plant_context, **USER_CONFIG)
            
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