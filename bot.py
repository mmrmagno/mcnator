import discord
import asyncio
import json
import re
import os
from discord.ext import commands
from mcrcon import MCRcon

# Load token and channel ID from config.json
with open("config.json") as config_file:
    config = json.load(config_file)

TOKEN = config["TOKEN"]
CHANNEL_ID = config["CHANNEL_ID"]
LOG_FILE = "./data/logs/latest.log"
COORDS_FILE = "coords.json"
RCON_HOST = "172.18.0.7"
RCON_PORT = 25575
RCON_PASSWORD = config["RCON_PASSWORD"]

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="/", intents=intents)

# Regex patterns
chat_pattern = r"<(\w+)> discord (.+)"

death_pattern = (
    r"(\w+) (?:was pricked to death|walked into a cactus while trying to escape \w+|"
    r"drowned|drowned while trying to escape \w+|died from dehydration|"
    r"died from dehydration while trying to escape \w+|experienced kinetic energy|"
    r"experienced kinetic energy while trying to escape \w+|blew up|"
    r"was blown up by \w+|was blown up by \w+ using .*|was killed by \[Intentional Game Design\]|"
    r"hit the ground too hard|hit the ground too hard while trying to escape \w+|"
    r"fell from a high place|fell off a ladder|fell off some vines|"
    r"fell off some weeping vines|fell off some twisting vines|fell off scaffolding|"
    r"fell while climbing|was doomed to fall|was doomed to fall by \w+|"
    r"was doomed to fall by \w+ using .*|was impaled on a stalagmite|"
    r"was impaled on a stalagmite while fighting \w+|was squashed by a falling anvil|"
    r"was squashed by a falling block|was skewered by a falling stalactite|went up in flames|"
    r"walked into fire while fighting \w+|burned to death|was burned to a crisp while fighting \w+|"
    r"went off with a bang|went off with a bang due to a firework fired from .* by \w+|"
    r"tried to swim in lava|tried to swim in lava to escape \w+|"
    r"was struck by lightning|was struck by lightning while fighting \w+|"
    r"discovered the floor was lava|walked into the danger zone due to \w+|"
    r"was killed by magic|was killed by magic while trying to escape \w+|"
    r"was killed by \w+ using magic|froze to death|was frozen to death by \w+|"
    r"was slain by \w+|was slain by \w+ using .*|was stung to death|"
    r"was stung to death by \w+ using .*|was obliterated by a sonically-charged shriek|"
    r"was obliterated by a sonically-charged shriek while trying to escape \w+ wielding .*|"
    r"was shot by \w+|was shot by \w+ using .*|was pummeled by \w+|"
    r"was pummeled by \w+ using .*|was fireballed by \w+|was fireballed by \w+ using .*|"
    r"was shot by a skull from \w+|was shot by a skull from \w+ using .*|"
    r"starved to death|starved to death while fighting \w+|suffocated in a wall|"
    r"suffocated in a wall while fighting \w+|was squished too much|was squashed by \w+|"
    r"left the confines of this world|left the confines of this world while fighting \w+|"
    r"was poked to death by a sweet berry bush|was poked to death by a sweet berry bush while trying to escape \w+|"
    r"was killed while trying to hurt \w+|was killed by .* while trying to hurt \w+|"
    r"was impaled by \w+|was impaled by \w+ with .*|fell out of the world|"
    r"didn't want to live in the same world as \w+|withered away|withered away while fighting \w+|"
    r"died|died because of \w+|was killed|didn't want to live as \w+|"
    r"fell off a ladder and got finished off by \w+|fell off some vines and got finished off by \w+|"
    r"fell from a high place and got finished off by \w+)"
)
coords_pattern = r"<(\w+)> coords (\w+) (-?\d+) (-?\d+) (-?\d+)"
# Regex patterns for teleport log lines
tp_to_coord_pattern = r"\[\d{2}:\d{2}:\d{2}\] \[Server thread/INFO\]: \[(\w+): Teleported (\w+) to (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\]"
tp_to_player_pattern = r"\[\d{2}:\d{2}:\d{2}\] \[Server thread/INFO\]: \[(\w+): Teleported (\w+) to (\w+)\]"
achievement_pattern = (
    r"(\w+) has (?:made the advancement|reached the goal|completed the challenge) \[(.+)\]"
)


@bot.event
async def on_ready():
    """Bot startup event."""
    print(f"Logged in as {bot.user}")
    # Sync slash commands with Discord
    try:
        await bot.tree.sync()
        print("Slash commands synced!")
    except Exception as e:
        print(f"Error syncing commands: {e}")

def load_coords():
    """Load saved coordinates from file."""
    try:
        with open(COORDS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_coords(coords):
    """Save coordinates to file."""
    with open(COORDS_FILE, "w") as file:
        json.dump(coords, file, indent=4)


def get_skin_url(player_name):
    """Get the Minecraft player's skin head thumbnail URL."""
    return f"https://minotar.net/helm/{player_name}/100.png"


async def send_to_channel(embed=None):
    """Send an embed message to the Discord channel."""
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        try:
            await channel.send(embed=embed)
        except Exception as e:
            print(f"Failed to send message: {e}")
    else:
        print(f"Channel not found with ID: {CHANNEL_ID}")


async def monitor_server_logs():
    """Monitor Minecraft server logs for events."""
    try:
        print(f"Monitoring server logs at: {LOG_FILE}")
        coords_data = load_coords()
        server_online = True

        while True:
            if not os.path.exists(LOG_FILE):
                print("Waiting for server to come back online...")
                await asyncio.sleep(5)
                continue

            with open(LOG_FILE, "r") as log_file:
                log_file.seek(0, os.SEEK_END)
                while server_online:
                    line = log_file.readline()
                    if not line:
                        await asyncio.sleep(0.1)
                        continue

                    print(f"Log line: {line.strip()}")

                    # Handle death events
                    if match := re.search(death_pattern, line):
                        player, cause = match.group(1), line.split(match.group(1))[1].strip()
                        embed = discord.Embed(
                            description=f"💀 **{player}** {cause}",
                            color=discord.Color.dark_red(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle player joins
                    elif "joined the game" in line:
                        player = line.split()[3]
                        embed = discord.Embed(
                            description=f"✅ **{player}** joined the game!",
                            color=discord.Color.green(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle player leaves
                    elif "left the game" in line:
                        player = line.split()[3]
                        embed = discord.Embed(
                            description=f"❌ **{player}** left the game!",
                            color=discord.Color.red(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle coordinates
                    elif match := re.search(coords_pattern, line):
                        player, place, x, y, z = match.groups()
                        coords_data[place] = f"{x}, {y}, {z}"
                        save_coords(coords_data)
                        embed = discord.Embed(
                            description=f"📌 **{player}** saved coords for **{place}**: `{x}, {y}, {z}`",
                            color=discord.Color.blue(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle teleport to coordinates
                    elif match := re.search(tp_to_coord_pattern, line):
                        player, target, x, y, z = match.groups()
                        embed = discord.Embed(
                            description=f"🌀 **{player}** teleported **{target}** to `{x}, {y}, {z}`",
                            color=discord.Color.purple(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle teleport to another player
                    elif match := re.search(tp_to_player_pattern, line):
                        player, target, destination = match.groups()
                        embed = discord.Embed(
                            description=f"🌀 **{player}** teleported **{target}** to **{destination}**",
                            color=discord.Color.purple(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle achievements
                    elif match := re.search(achievement_pattern, line):
                        player, achievement = match.groups()
                        embed = discord.Embed(
                            description=f"🏆 **{player}** unlocked: **{achievement}**",
                            color=discord.Color.gold(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)

                    # Handle server stop
                    elif "Stopping the server" in line:
                        server_online = False
                        embed = discord.Embed(
                            description="🔴 **The Minecraft server is now offline!**",
                            color=discord.Color.red(),
                        )
                        await send_to_channel(embed=embed)

                    elif match := re.search(chat_pattern, line):
                        player, message = match.groups()
                        embed = discord.Embed(
                            description=f"💬 **{player}**: {message}",
                            color=discord.Color.blue(),
                        )
                        embed.set_thumbnail(url=get_skin_url(player))
                        await send_to_channel(embed=embed)
                    # Log unmatched lines for debugging
                    else:
                        print(f"Unmatched log line: {line.strip()}")

            # Check periodically for server restart
            while not os.path.exists(LOG_FILE) or not server_online:
                print("Waiting for server to come back online...")
                await asyncio.sleep(5)

                # Check if the server has restarted
                if os.path.exists(LOG_FILE):
                    with open(LOG_FILE, "r") as log_file:
                        for line in log_file.readlines():
                            if "Done" in line:
                                print("Server is back online!")
                                embed = discord.Embed(
                                    description="🟢 **The Minecraft server is now online!**",
                                    color=discord.Color.green(),
                                )
                                await send_to_channel(embed=embed)
                                server_online = True
                                break

    except Exception as e:
        print(f"Error: {e}")


@bot.tree.command(name="coords", description="Get saved player coordinates.")
async def coords(interaction: discord.Interaction, place: str):
    """Retrieve coordinates for a saved place."""
    coords_data = load_coords()
    if place in coords_data:
        await interaction.response.send_message(
            f"📌 Coords for **{place}**: `{coords_data[place]}`"
        )
    else:
        await interaction.response.send_message(
            f"❌ No coordinates found for **{place}**."
        )

@bot.tree.command(name="say", description="Send a message to Minecraft players.")
async def say(interaction: discord.Interaction, message: str):
    """Send a message to the Minecraft server."""
    try:
        with MCRcon(RCON_HOST, RCON_PASSWORD, port=RCON_PORT) as mcr:
            mcr.command(f"say {message}")
        await interaction.response.send_message(
            f"✅ Message sent to the server: {message}"
        )
    except Exception as e:
        await interaction.response.send_message(f"❌ Failed to send message: {e}")

bot.run(TOKEN)
