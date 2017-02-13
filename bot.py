import discord
from discord.ext import commands
from utils import output
import os, json

description = '''Netcoin tip bot'''
bot = commands.Bot(command_prefix='!', description=description)

with open("config.json",'r') as f:
    config = json.loads(f.read())            


startup_extensions = os.listdir("./cogs")
if "__pycache__" in startup_extensions:
    startup_extensions.remove("__pycache__")

output.info("Loading {} extension(s)...".format(len(startup_extensions)))


@bot.event
async def on_ready():
    loaded_extensions = []
    for extension in startup_extensions:
        try:
            bot.load_extension("cogs."+extension.replace(".py",""))
            loaded_extensions.append(extension)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n\t->{}'.format(extension, exc))
    output.success("Successfully loaded the following extension(s); "+str(loaded_extensions))

def is_owner(ctx):
    return ctx.message.author.id in config["owners"]
            
@bot.command(pass_context=True)
@commands.check(is_owner)
async def load(ctx, module:str):
    author = str(ctx.message.author)
    try:
        bot.load_extension("cogs."+module)
        output.info(author + " loaded module: " + module)
        await bot.say("Successfully loaded {}.py".format(module))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))

    
@bot.command(pass_context=True)
@commands.check(is_owner)
async def unload(ctx, module:str):
    author = str(ctx.message.author)
    try:
        bot.unload_extension("cogs."+module)
        output.info(author+" unloaded module: "+module)
        await bot.say("Successfully unloaded {}.py".format(module))
    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))
    
bot.run(config["token"])
