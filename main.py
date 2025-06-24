import os
import random
import sqlite3
from dotenv import load_dotenv
import discord
import string
import re

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True


#preprocessing
message_count = 0
message_limit = random.randint(5, 10)
conn = sqlite3.connect('messages.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT,
    content TEXT
)
''')
conn.commit()

vocab_conn = sqlite3.connect('vocab.db')
vocab_cursor = vocab_conn.cursor()
vocab_cursor.execute('''
CREATE TABLE IF NOT EXISTS vocab (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word TEXT UNIQUE
)
''')
vocab_conn.commit()



#bot
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
    cards = ['Ace', 'Two', "Three", 'Four','Five','Six','Seven','Eight','Nine','Ten','Jack','Queen','King']
    values = [11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]

    def hand_value(hand):
        total = sum(values[i] for i in hand)
        aces = hand.count(0)
        while total > 21 and aces:
            total -= 10
            aces -= 1
        return total

    player_hand = [random.randint(0, 12), random.randint(0, 12)]
    cpu_score = int(random.gauss(19, 2.5))
    cpu_score = max(16, min(cpu_score, 24))

    embed = discord.Embed(
        title="Cirno's Blackjack",
        description="Welcome to Cirno's Blackjack! Can you beat the strongest ice fairy?",
        color=discord.Color.blue()
    )
    embed.add_field(
        name="Your Hand",
        value=", ".join(cards[i] for i in player_hand) + f"\nTotal: {hand_value(player_hand)}",
        inline=False
    )
    embed.set_footer(text="🟩 = Hit | 🟥 = Stand")

    message = await ctx.respond(embed=embed)
    msg = await message.original_response()
    await msg.add_reaction("🟩")  # Hit
    await msg.add_reaction("🟥")  # Stand

    finished = False
    while not finished:
        def check(reaction, user):
            return (
                user == ctx.author and
                reaction.message and reaction.message.id == msg.id and
                str(reaction.emoji) in ["🟩", "🟥"]
            )
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
        except Exception:
            embed.description = "Timed out! Game ended."
            await msg.edit(embed=embed)
            return

        if str(reaction.emoji) == "🟥":
            finished = True
        elif str(reaction.emoji) == "🟩":
            player_hand.append(random.randint(0, 12))
            if hand_value(player_hand) > 21:
                finished = True

        # Update embed
        embed.clear_fields()
        embed.add_field(
            name="Your Hand",
            value=", ".join(cards[i] for i in player_hand) + f"\nTotal: {hand_value(player_hand)}",
            inline=False
        )
        await msg.edit(embed=embed)

    player_score = hand_value(player_hand)
    result = ""
    if player_score > 21 and cpu_score > 21:
        result = "Tie!"
    elif player_score > 21:
        result = "You Lose!"
    elif cpu_score > 21:
        result = "You Win!"
    elif player_score > cpu_score:
        result = "You Win!"
    elif player_score < cpu_score:
        result = "You Lose!"
    else:
        result = "Tie!"

    embed.description = f"Cirno had {cpu_score}. You had {player_score}.\n**{result}**"
    embed.set_footer(text="")
    await msg.edit(embed=embed)

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



@bot.slash_command(name="put", description="Add to the communal pot!")
async def put(ctx: discord.ApplicationContext, amount: int):
    if amount <= 0:
        await ctx.respond("Please put a positive amount!")
        return
    try:
        if not os.path.exists("pot.txt"):
            with open("pot.txt", "w") as f:
                f.write("0")
        with open("pot.txt", "r") as f:
            pot = int(f.read().strip())
        pot += amount
        with open("pot.txt", "w") as f:
            f.write(str(pot))
        await ctx.respond(f"You put {amount} in the pot! The pot now has {pot}.")
    except Exception as e:
        await ctx.respond("Something went wrong.")

@bot.slash_command(name="take", description="Take from the communal pot!")
async def take(ctx: discord.ApplicationContext, amount: int):
    if amount <= 0:
        await ctx.respond("Please take a positive amount!")
        return
    try:
        if not os.path.exists("pot.txt"):
            with open("pot.txt", "w") as f:
                f.write("0")
        with open("pot.txt", "r") as f:
            pot = int(f.read().strip())
        if amount > pot:
            await ctx.respond(f"Not enough in the pot! The pot only has {pot}.")
            return
        pot -= amount
        with open("pot.txt", "w") as f:
            f.write(str(pot))
        await ctx.respond(f"You took {amount} from the pot! The pot now has {pot}.")
    except Exception as e:
        await ctx.respond("Something went wrong.")

@bot.slash_command(name="pot", description="Check the communal pot!")
async def pot(ctx: discord.ApplicationContext):
    try:
        if not os.path.exists("pot.txt"):
            with open("pot.txt", "w") as f:
                f.write("0")
        with open("pot.txt", "r") as f:
            pot = int(f.read().strip())
        await ctx.respond(f"The pot currently has {pot}.")
    except Exception as e:
        await ctx.respond("Something went wrong.")


#print vocab
@bot.slash_command(name="vocab", description="Print all words in the vocab database.")
async def vocab(ctx: discord.ApplicationContext):
    vocab_cursor.execute('SELECT word FROM vocab ORDER BY word ASC')
    words = [row[0] for row in vocab_cursor.fetchall()]
    if not words:
        await ctx.respond("The vocab database is empty.")
        return
    # Discord message limit is 2000 chars
    vocab_text = ", ".join(words)
    if len(vocab_text) > 1900:
        short_vocab = ", ".join(words[:50]) + "..."
        await ctx.respond(f"Vocab too long to display ({len(words)} words). Showing first 50:\n{short_vocab}")
    else:
        await ctx.respond(vocab_text)

#test for ml
@bot.event
async def on_message(message):
    global message_count, message_limit

    if message.author == bot.user:
        return

    #message storing
    cursor.execute('''
    INSERT INTO messages (author, content)
    VALUES (?, ?)
    ''', (str(message.author), message.content))
    conn.commit()

    #vocab storing
    words = set(
        w.lower()
        for w in re.findall(r"\w+|[^\w\s]", message.content)
        if w and not w.isdigit()
    )
    for word in words:
        try:
            vocab_cursor.execute('INSERT OR IGNORE INTO vocab (word) VALUES (?)', (word,))
        except Exception:
            pass
    vocab_conn.commit()

    message_count += 1

    if message_count >= message_limit:
        cursor.execute('SELECT content FROM messages ORDER BY RANDOM() LIMIT 1')
        row = cursor.fetchone()
        if row:
            await message.channel.send(row[0])
        message_count = 0
        message_limit = random.randint(5, 15)



bot.run(TOKEN)