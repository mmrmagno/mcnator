import discord
import asyncio
import json
import re
from discord.ext import commands
from mcrcon import Mcrcon  # Install via pip: pip install mcrcon

# Load token and channel ID from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['TOKEN']
CHANNEL_ID = config['CHANNEL_ID']
RCON_HOST = "minecraft-server"  # RCON hostname (Docker service name)
RCON_PORT = 25575
RCON_PASSWORD = config['RCON_PASSWORD']

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    bot.loop.create_task(monitor_rcon_events())
    await bot.tree.sync()  # Ensure slash commands are registered

async def send_to_channel(message, embed=None):
    """Send a message to the Discord channel."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message, embed=embed)
    else:
        print("Failed to find Discord channel.")

async def monitor_rcon_events():
    """Monitor the Minecraft server via RCON for events."""
    try:
        with Mcrcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            print("Connected to RCON!")
            while True:
                response = mcr.command("list")  # Example command to keep connection alive
                print(f"RCON Response: {response}")
                await asyncio.sleep(5)  # Poll every 5 seconds
    except Exception as e:
        print(f"Error in RCON connection: {e}")

# Slash command for player coordinates
@bot.tree.command(name="coords", description="Get saved player coordinates.")
async def coords(interaction: discord.Interaction, player: str):
    coords_data = load_coords()
    if player in coords_data:
        await interaction.response.send_message(f"Coords for **{player}**: {coords_data[player]}")
    else:
        await interaction.response.send_message(f"No coordinates found for **{player}**.")

# Slash command for sending messages to Minecraft players
@bot.tree.command(name="say", description="Send a message to Minecraft players.")
async def say(interaction: discord.Interaction, message: str):
    try:
        with Mcrcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            mcr.command(f"say {message}")
        await interaction.response.send_message(f"Sent message to Minecraft players: {message}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to send message: {e}")

# Load and save coordinates
def load_coords():
    try:
        with open("coords.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_coords(coords):
    with open("coords.json", "w") as file:
        json.dump(coords, file, indent=4)

bot.run(TOKEN)
