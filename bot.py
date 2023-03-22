import json
import random
import re

from discord.ext import commands

from markovboi import MarkovBoi

m = MarkovBoi()

with open('secrets.json', 'r') as f:
    TOKEN = json.loads(f.read())['TOKEN']

bot = commands.Bot(command_prefix='!')


@bot.event
async def on_ready():
    """
    Function to handle the 'on_ready' event for a Discord bot.

    This function is triggered when the bot is ready to receive and respond to commands. It prints a message to the
        console indicating that the bot is online and ready to use.

    Returns:
        None
    """

    print(f'{bot.user} is in the house!!')


@bot.event
async def on_message(message):
    """
    Function to handle the 'on_message' event for a Discord bot.

    This function is triggered whenever a message is sent in a Discord channel that the bot has access to. It performs
    several tasks on the message, including printing its content to the console, parsing it with a 'm' object,
    processing any commands included in the message, and occasionally sending a generated message to the channel.

    Args:
        message (discord.Message): The message object containing the message content, author information, and other
        metadata.

    Returns:
        None
    """

    if message.author.bot:
        return

    print(message.content)

    m.parse_message(str(message.author.id), message.content)

    await bot.process_commands(message)

    if random.randint(1, 100) < 5:
        await message.channel.send(m.gen_message('000000000000000000'))


@bot.command()
async def scan(ctx):
    """
    Function to handle the 'scan' command for a Discord bot.

    This function is triggered whenever the 'scan' command is used in a Discord channel. It scans the last 10,000
    messages in the channel and indexes each non-bot message using a 'm' object. It then sends a message to the
    channel indicating how many messages were scanned and indexed.

    Args:
        ctx (discord.ext.commands.Context): The context object representing the context in which the command was used.
        Contains information about the message, author, and other metadata.

    Returns:
        None
    """
    count = 0

    async for msg in ctx.message.channel.history(limit=10000):
        if not msg.author.bot and not msg.content.startswith(('-', 's?', '!')):
            count += 1
            m.parse_message(str(msg.author.id), msg.content)

    await ctx.channel.send(f'last {count} messages in this channel scanned and indexed')


@bot.command()
async def copy(ctx, user=None, seed=None):
    """
    Function to handle the 'copy' command for a Discord bot.

    This function is triggered whenever the 'copy' command is used in a Discord channel. It takes an optional 'user'
    argument, which specifies which user's message history to copy, and an optional 'seed' argument, which is used
    to generate a specific message. If no user is specified, the function copies the message history of the user who
    invoked the command.

    Args:
        ctx (discord.ext.commands.Context): The context object representing the context in which the command was used.
        Contains information about the message, author, and other metadata.

        user (str, optional): A string representing the user ID of the user whose message history should be copied.
        Defaults to None.

        seed (str, optional): A string representing the seed used to generate a specific message. Defaults to None.

    Returns:
        None
    """
    if user and user.lower() == 'all':
        user = '000000000000000000'
    elif user:
        try:
            user = re.findall(r'\d{18}', user)[0]
        except IndexError:
            await ctx.channel.send('**error:** first arg must be a valid user or "all"')
    else:
        user = str(ctx.author.id)

    if len(user) != len(str(ctx.author.id)):
        return

    if seed:
        await ctx.channel.send(m.gen_message(user, seed))
    else:
        await ctx.channel.send(m.gen_message(user))


bot.run(TOKEN)
