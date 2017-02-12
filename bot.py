import discord
from discord.ext import commands
import os
import json

description = '''Netcoin tip bot''' 
bot = commands.Bot(command_prefix='!', description=description)

startup_extensions = os.listdir("./cogs")

@bot.event
async def on_ready():
    for extension in startup_extensions:
        try:
            bot.load_extension("cogs."+extension.replace(".py",""))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('Failed to load extension {}\n{}'.format(extension, exc))

with open("config.json",'r') as f:
    config = json.loads(f.read())            

bot.run(config["token"])