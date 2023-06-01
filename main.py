import os, keys, discord
import commands

TOKEN = keys.get("DISCORD_TOKEN")
BOT_CHANNELS_CONTAIN = "jump-command", "jumpedia"

intents = discord.Intents.default()
intents.message_content = True

try:
    client = discord.Client(intents=intents)
except:
    print('Bot crashed, restarting')
    os.system("kill 1")


def ping(id):
    return "<@" + str(id) + ">"


@client.event
async def on_ready():
    print('Bot online as {0.user}'.format(client))
    for guild in client.guilds:
        for channel in guild.channels:
            for container in BOT_CHANNELS_CONTAIN:
                if container in channel.name.lower() and isinstance(channel, discord.TextChannel):
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send("**Jumpedia is back online!**")
    await client.wait_until_ready()


@client.event
async def on_message(message):

    async def dcPrint(text):
        await message.channel.send(text)

    # Define some 'constants'
    author = message.author
    username = str(author).split('#')[0]
    msg = str(message.content)
    channel = str(message.channel.name)
    print(f'{username}: {msg} ({message.guild} -> {channel})')

    # Don't react to own messages
    if author == str(client.user):
        return

    # Images and pins
    if msg == '':
        return

    try:
        # Message handling
        for container in BOT_CHANNELS_CONTAIN:
            if container in channel:
                answer = commands.run(msg, author)
                if (answer):
                    await dcPrint(answer)

    except Exception as e:
        out = f'An exception (internal bug) has occurred! Please DM {ping(679564566769827841)} if he is not on the server!\nCommand that caused the exception:```{msg}```'

        await dcPrint(out)
        raise e


try:
    client.run(keys.get("DISCORD_TOKEN"))
#Bot Restarter
except discord.errors.HTTPException:
    print("\n\n\nBLOCKED BY RATE LIMITS\nRESTARTING NOW\n\n\n")
    os.system("restarter.py")
    os.system('kill 1')
