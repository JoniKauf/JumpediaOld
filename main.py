"""
The main module of the bot. This file is responsible for the bot's startup and
on message response.
"""

import os, secret, discord, json
import commands
from discord import Message
from discord import app_commands
from io import TextIOWrapper
import logging

DEVELOPMENT_MODE = False
DEVELOPMENT_CHANNEL_IDS = 1063371102547607552, 1161991190779011102

TOKEN = secret.get_key("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

try:
    client = discord.Client(intents=intents)
    tree = app_commands.CommandTree(client)
except:
    print('Bot crashed!')

def ping(id: int | str) -> str:
    return "<@" + str(id) + ">"

@tree.command(name = "testcommand", description = "The first slash command of Jumpedia for testing purposes!") #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction: discord.Interaction):
    await interaction.response.send_message("**Hello, this is a very cool slash command!**\nSoon all commands will work with slash commands! :D")

@client.event
async def on_ready():

    await tree.sync()

    await client.wait_until_ready()

    if DEVELOPMENT_MODE:
        for channel_id in DEVELOPMENT_CHANNEL_IDS:
            await client.get_channel(channel_id).send("**Development version of Jumpedia is running!**\nNo notification will be sent when it goes offline, so use it while it lasts!")

@client.event
async def on_message(message: Message):
    # Define some 'constants'
    author = message.author
    msg = str(message.content)

    # Don't react to own messages
    if author.id == client.user.id:
        return

    # Ignore empty messages, which includes images and pins
    if not msg: return

    try:
        if (DEVELOPMENT_MODE != (message.channel.id in DEVELOPMENT_CHANNEL_IDS)):
            return

        # Biggest module handling all commands
        await commands.run(message, client, DEVELOPMENT_MODE)

    except Exception as e:
        out = f'An exception (internal bug) has occurred! Please DM {ping(679564566769827841)} if he is not on the server!\nCommand that caused the exception:```{msg}```'

        await message.channel.send(out)
        raise e

client.run(TOKEN)

