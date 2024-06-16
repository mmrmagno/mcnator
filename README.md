# McNator

McNator is a Discord bot for monitoring and interacting with your Minecraft server. The bot provides various commands to track player activity, find slime chunks, locate village chunks, and roll dice.

## Features

- Real-time server monitoring: player join/leave notifications, achievements, deaths, and teleports.

- Display slime chunks around specified coordinates.

- Display village chunks around specified coordinates.

- Retrieve saved coordinates for places.

- Roll a random number within a specified range.

## Requirements

- Python 3.7+

- `discord.py` library

- `Pillow` library

## Installation

1\. Clone the repository:

    ```sh

    git clone https://github.com/yourusername/mcdiscbot.git

    cd mcdiscbot

    ```

2\. Install the required libraries:

    ```sh

    pip install discord.py pillow

    ```

3\. Configure your bot:

    - Open `bot.py` in a text editor.

    - Replace `YOUR_BOT_TOKEN` with your actual Discord bot token.

    - Replace `CHANNEL_ID` with the ID of the channel where you want to send notifications.

    - Optionally, update `COORDS_FILE` to specify a different path for storing coordinates.

4\. Run the bot:

    ```sh

    python3 bot.py

    ```

## Commands

### /slime `<seed> <x> <y> <z>`

Display a map highlighting slime chunks around the specified coordinates for the given seed.

**Usage Example:**

```sh

/slime 123456 100 64 200
