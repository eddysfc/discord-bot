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
    async for message in channel.history(limit=max(limit, n)):
        if user is None or message.author == user:
            messages.append(message)
        if len(messages) >= n:
            break
    return messages

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}.")
    await bot.sync_commands()
    
# hello
@bot.slash_command(name="hello", description="Say hello to the bot!")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(f"Hello, {ctx.author.display_name}!")

# blackjack
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

# ping
@bot.slash_command(name="ping", description="Check the bot's ping!")
async def ping(ctx):
    a = bot.latency * 1000
    if round(a) <= 50:
        embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(a)}** milliseconds!", color=0x44ff44)
    elif round(a) <= 100:
        embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(a)}** milliseconds!", color=0xffd000)
    elif round(a) <= 200:
        embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(a)}** milliseconds!", color=0xff6600)
    else:
        embed=discord.Embed(title="PING", description=f":ping_pong: Pingpingpingpingping! The ping is **{round(a)}** milliseconds!", color=0x990000)
    await ctx.respond(embed=embed)

@bot.slash_command(name="recent", description="Get the 10 most recent messages in the current channel.")
async def recent(ctx: discord.ApplicationContext, user: discord.User | None):
    messages = await fetch_recent_messages(ctx.channel, 10, user)
    for message in reversed(messages):
        print(f"{message.author.display_name}: {message.content}")
    await ctx.respond("Recent messages have been printed to the console.")


@bot.slash_command(name="stats", description="Check your message stats!")
async def stats(ctx: discord.ApplicationContext, range: int = 100):
    messages = await fetch_recent_messages(ctx.channel, range)
    userMessages = 0
    userChars = 0
    totalChars = 0
    for message in messages:
        if message.author == ctx.author:
            userMessages += 1
            userChars += len(message.content)
        totalChars += len(message.content)
    percentChars = 100 * userChars / totalChars
    response = f"Out of the {range} most recent messages, you sent {userMessages}!\nOf which, your messages occupied {percentChars:.3f}% of the total characters ({userChars} out of {totalChars})!\n"
    if percentChars >= 35:
        response += "Holy shit stop yapping already"
    elif percentChars >= 25:
        response += "You are the center of attention, good stuff"
    elif percentChars >= 15:
        response += "You contributions are respectfully appreciated"
    elif percentChars >= 5:
        response += "You should be more active... :("
    else:
        response += "L lurker lmao"
    await ctx.respond(response)

bot.run(TOKEN)