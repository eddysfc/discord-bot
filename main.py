import os
import random

from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

async def fetch_recent_messages(
    channel: discord.TextChannel,
    n: int = 10,
    user: discord.User | None = None,
    limit: int = 100,
):
    """
    Helper function to fetch the n most recent messages from a channel.

    Args:
        channel (discord.TextChannel): The channel to search in.
        n (int): Number of messages to fetch. Default is 10.
        user (discord.User | None): If provided, filter by this user.
        limit (int): How many messages back to search. Default is 100.
    
    Returns:
        list[discord.Message]: The list of messages.
    """
    messages = []
    async for message in channel.history(limit=limit):
        if user is None or message.author == user:
            messages.append(message)
        if len(messages) >= n:
            break
    return messages

@bot.event
async def on_ready():
    await bot.sync_commands()
    print(f"Bot is ready! Logged in as {bot.user}.")
    

@bot.slash_command(name="hello", description="Say hello to the bot!")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(f"Hello, {ctx.author.display_name}!")


@bot.slash_command(name="blackjack", description="Play a game of Blackjack with Cirno!")
async def blackjack(ctx):
    await ctx.respond("Welcome to Cirno's Blackjack! Can you beat the strongest ice fairy?")
    await ctx.channel.send("Dealing...")
    def check(msg):
        return msg.author == ctx.author and msg.channel == ctx.channel and msg.content in ["e", "E", "c", "C"]
    cards = ['Ace', 'Two', "Three", 'Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King']
    value=[11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
    x = random.randint(0,12)
    y = random.randint(0,12)
    h = ""
    msg = " "

    hand = [cards[x], cards[y]]
    handr = [x, y]
    handv = [value[x], value[y]]
    cpu = random.randint(17,24)
    await ctx.channel.send("Your current cards: "+hand[0]+", "+hand[1])

    while sum(handv)<22:
        await ctx.channel.send('Press E to end, Press C to continue')
        msg = await bot.wait_for("message", check=check)
        if msg.content == "e":
            break
        if msg.content== "E":
            break
        z = random.randint(0,13)
        hand.append(cards[z])
        handr.append(z)
        handv.append(value[z])
        h="New Hand: "
        for g in hand:
            h+=g+", "
        await ctx.channel.send(h)
        if (sum(handv)>21):
            value[0] = 1

        handv = []
        for x in handr:
            handv.append(value[x])   

    await ctx.channel.send("Cirno had "+str(cpu)+". You had "+str(sum(handv))+".")
    if sum(handv)>21 and cpu>21:
        await ctx.channel.send('Tie!')
    elif sum(handv)>21:
        await ctx.channel.send('You Lose!')
    elif cpu>21:
        await ctx.channel.send('You Win!')
    elif sum(handv)>cpu:
        await ctx.channel.send("You Win!")
    elif sum(handv)<cpu:
        await ctx.channel.send('You Lose!')
    else:
        await ctx.channel.send('Tie!')

bot.run(TOKEN)