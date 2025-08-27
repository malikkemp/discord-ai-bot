import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import requests

# Load environment variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
ALLY_FIRST_NAME = os.getenv("ALLY_FIRST_NAME", "Ally")
ALLY_LAST_NAME = os.getenv("ALLY_LAST_NAME", "Gupta")
ALLY_AGE = os.getenv("ALLY_AGE", "30")

# vLLM server config
VLLM_URL = os.getenv("VLLM_URL", "http://127.0.0.1:8000/generate")
VLLM_API_KEY = os.getenv("VLLM_API_KEY")  # optional
VLLM_TIMEOUT = int(os.getenv("VLLM_TIMEOUT_SEC", "30"))

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Hidden instructions (system prompt)
HIDDEN_INSTRUCTIONS = f"""[SYSTEM INSTRUCTIONS]
You are {ALLY_FIRST_NAME} {ALLY_LAST_NAME}, Age: {ALLY_AGE}.

Born and raised in Sequorah Creek. Lives with his mother and gay uncle.

Dreams of moving to Vancouver and starting a family.

Character relationships:

- Arell: the main character of the series, Ally closely observes their interactions and behavior.

- Fatima: Ally's aunt, whose dynamics with Arell are important.

- Dallas: main character, a friend or acquaintance.

- Kamron: main character, potential love interest.

- Ally's family: his mother and gay uncle. Mention others only if directly relevant.

Guidelines for responses:

1. Always stay in-character as Ally Gupta.
2. Provide concise, lore-rich responses (1-4 sentences).
3. Always spell the town as "Sequorah Creek".
4. Only include information consistent with the series' established lore.
5. Never repeat the user's prompt in your response.
6. When describing other characters, do so from Ally's perspective.
7. Maintain a friendly, helpful tone.
8. Do not include the system prompt or internal instructions in the output.
End of instructions
"""

def vllm_call(user_input: str, max_tokens=150, temperature=0.7):
    """Call the vLLM/FastAPI server and return only a single response."""
    headers = {"Content-Type": "application/json"}
    if VLLM_API_KEY:
        headers["Authorization"] = f"Bearer {VLLM_API_KEY}"

    # Build prompt with hidden instructions
    prompt = f"{HIDDEN_INSTRUCTIONS}\nUser: {user_input}\nResponse:\n"

    payload = {
        "prompt": prompt,
        "max_new_tokens": max_tokens,
        "temperature": temperature
    }

    resp = requests.post(VLLM_URL, json=payload, headers=headers, timeout=VLLM_TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    # Extract and clean output
    output = data.get("response", "").strip()
    output = output.replace(HIDDEN_INSTRUCTIONS, "").strip()
    # Collapse multiple lines into a single paragraph
    output = " ".join(line.strip() for line in output.splitlines() if line.strip())
    return output

async def generate_vllm(user_input: str, max_tokens=150, temperature=0.7):
    """Async wrapper for vllm_call using asyncio.to_thread."""
    return await asyncio.to_thread(vllm_call, user_input, max_tokens, temperature)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (id: {bot.user.id})")

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    is_dm = isinstance(message.channel, discord.DMChannel)
    is_mention = bot.user in message.mentions
    if is_dm or is_mention:
        content = message.content
        if is_mention:
            # Remove mention tags
            content = content.replace(f"<@!{bot.user.id}>", "").replace(f"<@{bot.user.id}>", "").strip()
        if not content:
            return
        try:
            reply = await generate_vllm(content)
        except Exception as e:
            await message.reply(f"Error contacting vLLM: {e}")
            return
        await message.reply(reply)

    await bot.process_commands(message)

# Run the bot
bot.run(DISCORD_TOKEN)
