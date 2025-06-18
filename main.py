import os

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
    print(f"Bot is ready! Logged in as {bot.user}.")

@bot.slash_command(name="hello", description="Say hello to the bot!")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond(f"Hello, {ctx.author.display_name}!")

bot.run(TOKEN)