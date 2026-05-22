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

## Complete AI Plant Bot Project - Full Stack Deployment

### What I Built
A fully functional AI plant care agent running 24/7 on Render that:
- Sends daily plant watering reminders via Telegram at 8 AM
- Responds to user questions in real-time via two-way Telegram chat
- Tracks 40+ plants with watering schedules
- Uses Claude AI with custom system prompt and soil metrics
- Executes tools to update database based on user actions

### The 5 Phases

**Phase 1: LLM Fundamentals**
- Built CLI chatbot with Claude API
- Learned: API calls, system prompts, message history, token counting
- Key insight: Claude is stateless; you control context by passing messages

**Phase 2: Memory & State**
- Created SQLite database with plant tracking
- Learned: Database schema, SQL queries, persistent memory
- Key insight: Databases are the source of truth; inject data into prompts dynamically

**Phase 3: Tool Use (Agent Loop)**
- Implemented function calling with Claude
- Tools: update_water_date, get_plants_needing_water, log_observation, add_plant
- Learned: Agent loop pattern (user → Claude → tool decision → execute → respond)
- Key insight: This pattern is the foundation of all AI agents

**Phase 4: Proactive Agent**
- Added APScheduler for background tasks
- Bot proactively checks plants daily without user prompting
- Learned: Scheduling, background processes, combining reactive + proactive AI
- Key insight: Most real AI agents are proactive, not just reactive

**Phase 5: Deployment & Two-Way Telegram**
- Deployed to Render (cloud hosting)
- Added Telegram polling for incoming messages
- Two-way chat: receive messages → send to Claude → send response back
- Learned: Cloud deployment, environment variables, Telegram Bot API, webhooks vs polling
- Key insight: Production AI requires proper architecture (where to run, how to persist state, monitoring)

### Technical Learnings

**Prompt Engineering**
- Tested different tones, lengths, expertise levels
- Discovered: Cheaper models with thinking can match expensive models
- Removing "concise" constraint helped quality
- Best approach: XML-structured prompts for clarity

**Database Design**
- Normalized schema with plants table
- Dynamic context injection: build_plant_context() pulls fresh data each request
- Added soil metrics as variables in prompt

**Token Optimization**
- System prompt + message history sent every request
- Long conversations cost more
- Prompt caching (90% discount) and summarization for optimization

**Version Control & Deployment**
- Git workflow: commit frequently with descriptive messages
- GitHub as central source of truth
- Render auto-deploys on push
- Environment variables for secrets

**Two-Way Telegram Integration**
- Polling method: check for updates every 2 seconds
- Track last_update_id to avoid duplicates
- Separate concerns: notifications vs chat handlers
- Shared prompt system (prompts.py) used across modules

### Architecture Decisions

Created modular structure:
- `prompts.py` — centralized system prompt + config (DRY principle)
- `database.py` — all database operations
- `tools.py` — function definitions for Claude
- `scheduler.py` — background task scheduling
- `telegram_notifications.py` — one-way notifications
- `telegram_handler.py` — two-way chat handling
- `scheduler_only.py` — production entry point

### Key Insights Gained

1. **LLMs are tools, not magic** — they're predictable, require careful context management
2. **Agent loops are simple but powerful** — user input → AI decision → tool execution → response
3. **Context is everything** — injecting right data (plants, soil, weather) makes Claude much better
4. **Production is different** — local testing ≠ cloud deployment (stdin/stdout issues, environment variables, scaling)
5. **Empirical learning** — prompt engineering taught me why testing matters; small changes have big effects

### What's Next (Future Enhancements)
- Weather API integration for smart watering adjustments
- Image analysis via Telegram (upload plant photos)
- Customizable reminder times per plant
- Web dashboard to visualize plant history
- Multi-user support (group chats)

### Statistics
- **40+ plants** tracked in database
- **5 Claude tools** implemented
- **2 Telegram integrations** (notifications + chat)
- **1 cloud deployment** (Render)
- **0 dollars spent** (free tier)

### Conclusion
Built a production-ready AI agent from scratch. Learned that modern AI isn't about one big model—it's about architecture: combining LLMs with databases, scheduling, and APIs. The bot is simple in concept but demonstrates every major pattern used in real AI products.