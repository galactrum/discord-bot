from lib import discord
from utils import output, parsing

output = output.PrOut()

description = """Core module/initial Discord connection
Connecting using the token found in config.json"""

bot = discord.Client()

@bot.event
async def on_ready():
    output.info('Logged in as '+bot.user.name)

try:
    token = parsing.parse_json('config.json')["data"][0]["token"]
    bot.run(token)
except KeyboardInterrupt:
    output.success('KeyboardInterrupt: Shutting down bot...')