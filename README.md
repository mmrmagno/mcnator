McNator 
=====================

Introduction
------------

  ![McNator Logo](https://www.marc-os.com/src/banner-bot.png)

Welcome to McNator! McNator is a powerful Discord bot designed to enhance your Minecraft server experience. Developed by **mmrmagno aka Marc**, this bot provides real-time server monitoring, coordinates tracking, and special chunk mapping for slime and village chunks. McNator also includes a fun dice roll feature for random number generation.

Features
--------

### Real-time Server Monitoring

-   **Player Join/Leave Notifications**: Get notified when players join or leave your server.
-   **Achievements**: Track and announce player achievements.
-   **Deaths**: Get notifications when a player dies, including the cause of death.
-   **Teleports**: Monitor teleport activities with exact coordinates.
-   **Server Start/Stop Notifications**: Know when your server starts or stops.

### Chunk Mapping

-   **Slime Chunks**: Visualize slime chunks around specified coordinates.
-   **Village Chunks**: Identify village chunks around specified coordinates.

### Coordinates Tracking

-   **Save and Retrieve Coordinates**: Save important places and retrieve their coordinates on demand.

### Dice Roll

-   **Random Number Generation**: Roll a random number between a specified range or the default range (1-100).

Getting Started
---------------

### Requirements

-   Python 3.7+
-   `discord.py` library
-   `Pillow` library

### Installation

1.  **Clone the Repository**
 
    ```sh
    git clone https://github.com/yourusername/mcdiscbot.git
    cd mcdiscbot
    ```

2.  **Install the Required Libraries**

    ```sh
    pip -r install requirements.txt
    ```

4.  **Configure Your Bot**

    -   Open `bot.py` in a text editor.
    -   Replace `YOUR_BOT_TOKEN` with your actual Discord bot token.
    -   Replace `CHANNEL_ID` with the ID of the channel where you want to send notifications.
    -   Optionally, update `COORDS_FILE` to specify a different path for storing coordinates.
5.  **Run the Bot**    

    ```sh
    python3 bot.py
    ```

Commands
--------

### /slime `<seed> <x> <y> <z>`

**Description**: Display a map highlighting slime chunks around the specified coordinates for the given seed.

**Usage**:

```sh
/slime 123456 100 64 200
```

### /village `<seed> <x> <y> <z>`

**Description**: Display a map highlighting village chunks around the specified coordinates for the given seed.

**Usage**:

```sh
/village 123456 100 64 200
```

### /coords `<place>`

**Description**: Retrieve the coordinates for a saved place.

**Usage**:


```sh
/coords home
```

### /roll `[min] [max]`

**Description**: Roll a random number between `min` and `max` (default range is 1-100).

**Usage**:

```sh
/roll 1 100
```

### /commands

**Description**: List all available commands and their descriptions.

**Usage**:

```sh
/commands
```

Real-time Server Monitoring
---------------------------

McNator monitors the Minecraft server log and sends notifications for various events:

-   **Player Join/Leave**: Notifies when players join or leave the server.
-   **Achievements**: Announces player achievements.
-   **Deaths**: Sends notifications for player deaths along with the cause.
-   **Teleports**: Logs teleport activities with coordinates.
-   **Server Start/Stop**: Alerts when the server starts or stops.

### Configuration

**Server Log Path**: Update the `log_file_path` variable in the `monitor_minecraft_logs()` function to the path of your Minecraft server log file.

Contributing
------------

We welcome contributions! Feel free to submit issues, fork the repository, and send pull requests. Your contributions can help make McNator even better.

About the Developer
-------------------

Developed by [mmrmagno aka Marc](https://github.com/mmrmagno). For any inquiries or support, feel free to reach out on GitHub.
