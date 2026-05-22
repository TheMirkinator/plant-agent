# Week 1 
# Day 1 
- I learned how to use the mac terminal to create folders and install homebrew + python packages. 
- I downloaded VScode and learned how to create folders and access folders
- I created a Claude Console account which is seperate from Claude code etc. ai that i pay for monthly. That is the chat bot
whereas the console is the way you can purchase credits to use the claude API in your own code. You can see usage there and a whole bunch 
of other features I will likely learn about later. 
- Finally I made my first API call, asking the chat how often i need to water Star jasmine:  Water Star Jasmine when the top inch of soil feels dry to the touch—usually every 7-10 days, but this varies by season and pot size. During growing season (spring/summer) it'll need more frequent watering; in winter, let it dry out a bit more between waterings. Always check the soil first rather than watering on a fixed schedule, since overwatering is the quickest way to cause root rot.
# Day 1 
Added a SQLite database to remember plants. Claude can now see my plant collection in the system prompt.
Tested adding a Monstera and Claude recognized it, knew the watering schedule, and gave specific care tips.
Learned how to inject dynamic data into system prompts — this is how real AI apps personalize responses.
Next: Tool use — make Claude able to UPDATE the database when I water plants.

# Day 2
## Prompt Engineering Experiments
Discovered that thinking is a game-changer for cheaper models.
Haiku with thinking performs almost as well as Opus without it.
Key difference: Opus explores alternatives and edge cases; Haiku gives practical direct answers.
For the plant bot, Haiku is actually better — users want speed, not technical depth.

# Day 3 
Built a more sophisticated system prompt using XML tags for structure.
Successfully injecting plant data and soil test data into every conversation.
Claude now sees the user's specific context and can give personalized advice.
Next: Tool use — letting Claude modify the database.

## Tool creation and usage
Created a set of tools for the bot to use when a related text was provided by the user. We have an add plant tool that adds plant names, both regular and scientific as well as how often they need to be watered into the databse. Also we have tools to edit watering days in the db. I learned that this can be helpful for the LLM to keep track of data across conversations. The bot can now take actions not just return text. Also increased max tokens to 2048. 

## Day 4: Proactive Agent with Scheduling
Built a background scheduler using APScheduler.
Bot now proactively checks plants daily at 8 AM and generates personalized notifications.
Learned: Proactive agents initiate action; reactive agents respond to user input.
Next: Phase 5 — Telegram integration (deploy bot to Telegram so it actually sends notifications).