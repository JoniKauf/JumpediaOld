"""
The main module of the bot. This file is responsible for the bot's startup and
on message response.
"""


import os, secret, discord, json
import commands
from discord import Message
from io import TextIOWrapper

TOKEN = secret.get_key("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.message_content = True

try:
    client = discord.Client(intents=intents)
except:
    print('Bot crashed, restarting')
    os.system("kill 1")


def ping(id: int | str) -> str:
    return "<@" + str(id) + ">"


@client.event
async def on_ready():
    #await client.get_channel(469869606018744340).send("NottNiickk3#5320")
    print('Bot online as {0.user}'.format(client))

    # Write into every channel with at least command permissions
    with open(commands.CHANNEL_TYPES_FILE) as f:
        for str_channel_id, type in json.load(f).items():
            channel = client.get_channel(int(str_channel_id))

            if type > 0 and isinstance(channel, discord.TextChannel):
                if channel.permissions_for(channel.guild.get_member(client.user.id)).send_messages:
                    pass
                    #await channel.send("**Jumpedia is back online!**")

    await client.wait_until_ready()


@client.event
async def on_message(message: Message):
    async def dcPrint(text=None, file_path=None):
        if file_path:
            with open(file_path, "rb") as f:
                await message.channel.send(text, file=discord.File(f, filename=os.path.basename(file_path)))
                
        else:
            await message.channel.send(text)

    # Define some 'constants'
    author = message.author
    username = str(author).split('#')[0]
    msg = str(message.content)
    channel = str(message.channel.name)
    print(f'{author.global_name}: {msg} ({message.guild} -> {channel})')

    # Don't react to own messages
    if author == str(client.user):
        return

    # Images and pins
    if not msg: return

    try:
        # Debugging, only allow #jumpedia-spam channel
        # if message.channel.id != 1063371102547607552: return
        
        # Message handling
        answer = commands.run(message, client)
        if not answer:
            return
        
        if isinstance(answer, str):
            await dcPrint(text=answer)
        elif isinstance(answer, tuple):
            await dcPrint(text=answer[0], file_path=answer[1])

    except Exception as e:
        out = f'An exception (internal bug) has occurred! Please DM {ping(679564566769827841)} if he is not on the server!\nCommand that caused the exception:```{msg}```'

        await dcPrint(out)
        raise e


try:
    client.run(secret.get_key("DISCORD_TOKEN"))
#Bot Restarter
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system("restarter.py")
    os.system('kill 1')
