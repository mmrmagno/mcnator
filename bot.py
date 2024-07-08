import discord
import re
import asyncio
import json
import random
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

# Load token and channel ID from config.json
with open('config.json') as config_file:
    config = json.load(config_file)

TOKEN = config['TOKEN']
CHANNEL_ID = config['CHANNEL_ID']
COORDS_FILE = 'coords.json'

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    bot.loop.create_task(monitor_minecraft_logs())
    await bot.tree.sync()  # Ensure the commands are registered

def load_coords():
    try:
        with open(COORDS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_coords(coords):
    with open(COORDS_FILE, 'w') as file:
        json.dump(coords, file, indent=4)

async def send_to_channel(message, embed=None):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(message, embed=embed)
        print(f'Sent message to channel: {message}')  # Debug statement
    else:
        print(f'Failed to find channel with ID {CHANNEL_ID}')  # Debug statement

def get_skin_url(player_name):
    return f"https://minotar.net/helm/{player_name}/100.png"

async def monitor_minecraft_logs():
    log_file_path = '/path/to/your/minecraft/logs/latest.log'

    with open(log_file_path, 'r') as file:
        file.seek(0, 2)

        while True:
            line = file.readline()
            if not line:
                await asyncio.sleep(1)
                continue

            print(f'Log Line: {line.strip()}')  # Debug statement to print the log line

            # Regex patterns for different events
            connect_pattern = r'\[.+\]: (\w+) joined the game'
            disconnect_pattern = r'\[.+\]: (\w+) left the game'
            achievement_pattern = r'\[.+\]: (\w+) has (?:made the advancement|reached the goal|completed the challenge) \[(.+)\]'
            death_pattern = r'\[.+\]: (\w+)(.*?(?:was slain by|was shot by|was blown up by|was fireballed by|was pummeled by|was impaled by|was skewered by|was squashed by|was pricked to death|was squished too much|suffocated in a wall|burned to death|starved to death|drowned|fell from a high place|fell out of the world|went up in flames|experienced kinetic energy|hit the ground too hard|fell off some vines|fell off a ladder|was impaled on a stalagmite|walked into a cactus while trying to escape|was doomed to fall|tried to swim in lava|died(?: by .*)?))'
            tp_pattern = r'\[.+\]: \[(\w+): Teleported (\w+) to (-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)\]'
            coords_pattern = r'<(\w+)> ([\w\s]+ -?\d+ -?\d+ -?\d+)'
            server_start_pattern = r'\[.+\]: Done \(.+?\)! For help, type "help" or "\?"'
            server_stop_pattern = r'\[.+\]: Stopping the server'

            if match := re.search(connect_pattern, line):
                player = match.group(1)
                skin_url = get_skin_url(player)
                embed = discord.Embed(description=f'**{player}** joined the game', color=discord.Color.green())
                embed.set_thumbnail(url=skin_url)
                await send_to_channel('', embed=embed)
                print(f'Matched Join: {player}')  # Debug statement

            elif match := re.search(disconnect_pattern, line):
                player = match.group(1)
                skin_url = get_skin_url(player)
                embed = discord.Embed(description=f'**{player}** left the game', color=discord.Color.red())
                embed.set_thumbnail(url=skin_url)
                await send_to_channel('', embed=embed)
                print(f'Matched Leave: {player}')  # Debug statement

            elif match := re.search(achievement_pattern, line):
                player, achievement = match.groups()
                skin_url = get_skin_url(player)
                embed = discord.Embed(description=f'**{player}** has reached the goal **[{achievement}]**', color=discord.Color.gold())
                embed.set_thumbnail(url=skin_url)
                await send_to_channel('', embed=embed)
                print(f'Matched Achievement: {player} - {achievement}')  # Debug statement

            elif match := re.search(death_pattern, line):
                player, cause = match.groups()
                cause = cause.strip()
                skin_url = get_skin_url(player)
                embed = discord.Embed(description=f'**{player}** {cause}', color=discord.Color.dark_red())
                embed.set_thumbnail(url=skin_url)
                await send_to_channel('', embed=embed)
                print(f'Matched Death: {player} {cause}')  # Debug statement

            elif match := re.search(tp_pattern, line):
                player, target, x, y, z = match.groups()
                skin_url = get_skin_url(player)
                embed = discord.Embed(description=f'**{player}** teleported **{target}** to coordinates **{x}, {y}, {z}**', color=discord.Color.blue())
                embed.set_thumbnail(url=skin_url)
                await send_to_channel('', embed=embed)
                print(f'Matched TP: {player} teleported {target} to {x}, {y}, {z}')  # Debug statement

            elif match := re.search(coords_pattern, line):
                player, coords = match.groups()
                coords_parts = coords.split()
                place = coords_parts[0]
                coords_values = " ".join(coords_parts[1:])
                skin_url = get_skin_url(player)
                embed = discord.Embed(description=f'Coords for **{place}**: {coords_values}', color=discord.Color.purple())
                embed.set_thumbnail(url=skin_url)
                await send_to_channel('', embed=embed)

                # Save coords to file
                coords_data = load_coords()
                coords_data[place] = coords_values
                save_coords(coords_data)
                print(f'Saved Coords: {place} - {coords_values}')  # Debug statement

            elif match := re.search(server_start_pattern, line):
                embed = discord.Embed(description='The server has started!', color=discord.Color.green())
                await send_to_channel('', embed=embed)
                print('Matched Server Start')  # Debug statement

            elif match := re.search(server_stop_pattern, line):
                embed = discord.Embed(description='The server is stopping!', color=discord.Color.red())
                await send_to_channel('', embed=embed)
                print('Matched Server Stop')  # Debug statement

@bot.command()
async def coords(ctx, *, place: str):
    coords_data = load_coords()
    if place in coords_data:
        await ctx.send(f'Coords for **{place}**: {coords_data[place]}')
    else:
        await ctx.send(f'No coordinates found for **{place}**.')

def is_slime_chunk(seed, x, z):
    import random
    random.seed(seed + (x * x * 0x4c1906) + (x * 0x5ac0db) + (z * z * 0x4307a7) + (z * 0x5f24f) ^ 0x3ad8025f)
    return random.randint(0, 9) == 0

def is_village_chunk(seed, x, z):
    # Simplified heuristic for village generation
    import random
    random.seed(seed + (x * 341873128712) + (z * 132897987541))
    return random.randint(0, 100) < 2  # 2% chance of village chunk

def generate_chunk_map(seed, x, z, radius=5, show_slime_chunks=True):
    chunk_x = x // 16
    chunk_z = z // 16
    size = (radius * 2 + 1) * 16
    image = Image.new('RGB', (size, size), (255, 255, 255))
    draw = ImageDraw.Draw(image)

    try:
        # Load a font
        font = ImageFont.truetype("arial.ttf", 10)
    except IOError:
        # If the font is not found, use the default font
        font = ImageFont.load_default()

    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            current_chunk_x = chunk_x + dx
            current_chunk_z = chunk_z + dz
            if show_slime_chunks:
                is_special = is_slime_chunk(seed, current_chunk_x, current_chunk_z)
                color = (0, 255, 0) if is_special else (255, 255, 255)
            else:
                is_special = is_village_chunk(seed, current_chunk_x, current_chunk_z)
                color = (255, 215, 0) if is_special else (255, 255, 255)
            top_left = ((dx + radius) * 16, (dz + radius) * 16)
            bottom_right = (top_left[0] + 15, top_left[1] + 15)
            draw.rectangle([top_left, bottom_right], fill=color, outline=(0, 0, 0))

    # Mark the player's position with a larger red dot
    player_pos = (radius * 16 + (x % 16), radius * 16 + (z % 16))
    draw.ellipse([player_pos[0] - 4, player_pos[1] - 4, player_pos[0] + 4, player_pos[1] + 4], fill=(255, 0, 0))

    # Add cardinal direction labels
    center = radius * 16
    draw.text((center, 2), "N", fill=(0, 0, 0), font=font)
    draw.text((center, size - 10), "S", fill=(0, 0, 0), font=font)
    draw.text((2, center), "W", fill=(0, 0, 0), font=font)
    draw.text((size - 10, center), "E", fill=(0, 0, 0), font=font)

    return image

@bot.command()
async def slime(ctx, seed: int = None, x: int = None, y: int = None, z: int = None):
    if None in (seed, x, y, z):
        embed = discord.Embed(title="Invalid Command Usage", description="Usage: /slime <seed> <x> <y> <z>", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        image = generate_chunk_map(seed, x, z, show_slime_chunks=True)
        image_path = f'/tmp/slime_chunk_map_{seed}_{x}_{z}.png'
        image.save(image_path)
        
        embed = discord.Embed(title="Slime Chunks", description=f"Seed: {seed}, Coordinates: {x}, {y}, {z}", color=discord.Color.green())
        embed.set_image(url=f"attachment://{image_path}")
        await ctx.send(file=discord.File(image_path), embed=embed)

        # Clean up the file after sending
        import os
        os.remove(image_path)

@bot.command()
async def village(ctx, seed: int = None, x: int = None, y: int = None, z: int = None):
    if None in (seed, x, y, z):
        embed = discord.Embed(title="Invalid Command Usage", description="Usage: /village <seed> <x> <y> <z>", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        image = generate_chunk_map(seed, x, z, show_slime_chunks=False)
        image_path = f'/tmp/village_chunk_map_{seed}_{x}_{z}.png'
        image.save(image_path)
        
        embed = discord.Embed(title="Village Chunks", description=f"Seed: {seed}, Coordinates: {x}, {y}, {z}", color=discord.Color.gold())
        embed.set_image(url=f"attachment://{image_path}")
        await ctx.send(file=discord.File(image_path), embed=embed)

        # Clean up the file after sending
        import os
        os.remove(image_path)

@bot.command(name="commands")
async def help_command(ctx):
    embed = discord.Embed(title="Help - Available Commands", color=discord.Color.blue())
    embed.add_field(name="/slime <seed> <x> <y> <z>", value="Show slime chunks around the given coordinates for the specified seed.", inline=False)
    embed.add_field(name="/village <seed> <x> <y> <z>", value="Show village chunks around the given coordinates for the specified seed.", inline=False)
    embed.add_field(name="/coords <place>", value="Retrieve the coordinates for a saved place.", inline=False)
    embed.add_field(name="/roll [min] [max]", value="Roll a random number between min and max (default 1-100).", inline=False)
    await ctx.send(embed=embed)

@bot.command()
async def roll(ctx, min: int = 1, max: int = 100):
    if min >= max:
        embed = discord.Embed(title="Invalid Command Usage", description="Usage: /roll [min] [max] - Ensure min is less than max.", color=discord.Color.red())
        await ctx.send(embed=embed)
    else:
        result = random.randint(min, max)
        embed = discord.Embed(title="Dice Roll", description=f"🎲 You rolled: **{result}** (range: {min}-{max})", color=discord.Color.blue())
        await ctx.send(embed=embed)

bot.run(TOKEN)
