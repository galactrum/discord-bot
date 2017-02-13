import discord
from discord.ext import commands
from utils import output
import os, json

description = '''Netcoin tip bot'''
bot = commands.Bot(command_prefix='!', description=description)

startup_extensions = os.listdir("./cogs")
output = output.PrOut()

output.info("Loading {} extensions...".format(len(startup_extensions)))


@bot.event
async def on_ready():
    loaded_extensions = []
    for extension in startup_extensions:
        try:
            bot.load_extension("cogs."+extension.replace(".py",""))
            loaded_extensions.append(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n{}'.format(extension, exc))
    output.success("Successfully loaded the following extensions; "+str(loaded_extensions))

with open("config.json",'r') as f:
    config = json.loads(f.read())            

bot.run(config["token"])