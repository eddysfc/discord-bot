import os

from dotenv import load_dotenv
import discord

load_dotenv()
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready! Logged in as {bot.user}.")

@bot.slash_command(name="hello", description="Say hello to the bot!")
async def hello(ctx):
    await ctx.respond(f"Hello, {ctx.author.display_name}!")

bot.run(TOKEN)