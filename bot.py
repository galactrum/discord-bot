import discord
from discord.ext import commands
from utils import output, parsing, checks
import os

description = '''Netcoin tip bot'''
bot = commands.Bot(command_prefix='!', description=description)

config = parsing.parse_json('config.json')


startup_extensions = os.listdir("./cogs")
if "__pycache__" in startup_extensions:
    startup_extensions.remove("__pycache__")


@bot.event
async def on_ready():
    output.info("Loading {} extension(s)...".format(len(startup_extensions)))
    loaded_extensions = []

    for extension in startup_extensions:
        try:
            bot.load_extension("cogs.{}".format(extension.replace(".py","")))
            loaded_extensions.append(extension)

        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n\t->{}'.format(extension, exc))

    output.success('Successfully loaded the following extension(s); {}'.format(loaded_extensions))


@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def shutdown(ctx):
    author = str(ctx.message.author)

    try:
        await bot.say("Shutting down...")
        await bot.logout()
        bot.loop.stop()
        output.info('{} has shut down the bot...'.format(author))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} has attempted to shut down the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc))


@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def load(ctx, module: str):
    author = str(ctx.message.author)

    try:
        bot.load_extension("cogs.{}".format(module))
        output.info('{} loaded module: {}'.format(author, module))
        await bot.say("Successfully loaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} attempted to load module \'{}\' but the following '
                     'exception occured;\n\t->{}'.format(author, module, exc))
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))

    
@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def unload(ctx, module: str):
    author = str(ctx.message.author)

    try:
        bot.unload_extension("cogs.{}".format(module))
        output.info('{} unloaded module: {}'.format(author, module))
        await bot.say("Successfully unloaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))


@bot.command(pass_context=True)
@commands.check(chekcs.is_owner)
async def restart(ctx):
    author = str(ctx.message.author)

    try:
        await bot.say("Restarting...")
        await bot.logout()
        bot.loop.stop()
        output.info('{} has restarted the bot...'.format(author))
        os.system('sudo sh restart.sh')

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} has attempted to restart the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc))

bot.run(config["discord"]["token"])
bot.loop.close()
