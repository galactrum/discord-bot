import discord
from discord.ext import commands
from utils import output, parsing, checks
import os

description = '''Netcoin Tipbot'''
bot = commands.Bot(command_prefix='!', description=description)

try:
    os.remove("log.txt")
except FileNotFoundError:
    pass

config = parsing.parse_json('config.json')


startup_extensions = os.listdir("./cogs")
if "__pycache__" in startup_extensions:
    startup_extensions.remove("__pycache__")
startup_extensions = [ext.replace('.py', '') for ext in startup_extensions]
loaded_extensions = []


@bot.event
async def on_ready():
    output.info("Loading {} extension(s)...".format(len(startup_extensions)))

    for extension in startup_extensions:
        try:
            bot.load_extension("cogs.{}".format(extension.replace(".py", "")))
            loaded_extensions.append(extension)

        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n\t->{}'.format(extension, exc))
    output.success('Successfully loaded the following extension(s); {}'.format(loaded_extensions))

async def send_cmd_help(ctx):
    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(title="Missing args :x:", description=page.strip("```").replace('<', '[').replace('>', ']'), color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(title="Missing args :x:", description=page.strip("```").replace('<', '[').replace('>', ']'), color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)


@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def shutdown(ctx):
    """Shut down the bot"""
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
    """Load a cog located in /cogs"""
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.load_extension("cogs.{}".format(module))
        output.info('{} loaded module: {}'.format(author, module))
        loaded_extensions.append(module)
        await bot.say("Successfully loaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} attempted to load module \'{}\' but the following '
                     'exception occured;\n\t->{}'.format(author, module, exc))
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))

    
@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def unload(ctx, module: str):
    """Unload any loaded cog"""
    author = str(ctx.message.author)
    module = module.strip()

    try:
        bot.unload_extension("cogs.{}".format(module))
        output.info('{} unloaded module: {}'.format(author, module))
        startup_extensions.remove(module)
        await bot.say("Successfully unloaded {}.py".format(module))

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        await bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))


@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def loaded(ctx):
    """List loaded cogs"""
    string = ""
    for cog in loaded_extensions:
        string += cog + "\n"

    await bot.say('Currently loaded extensions:\n```{}```'.format(string))


@bot.command(pass_context=True)
@commands.check(checks.is_owner)
async def restart(ctx):
    """Restart the bot"""
    author = str(ctx.message.author)

    try:
        await bot.say("Restarting...")
        await bot.logout()
        bot.loop.close()
        output.info('{} has restarted the bot...'.format(author))
        os.system('sudo sh restart.sh')

    except Exception as e:
        exc = '{}: {}'.format(type(e).__name__, e)
        output.error('{} has attempted to restart the bot, but the following '
                     'exception occurred;\n\t->{}'.format(author, exc))


@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        output.error("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original))
        oneliner = "Error in command '{}' - {}: {}\nIf this issue persists, Please report it in the support server.".format(ctx.command.qualified_name, type(error.original).__name__,str(error.original))
        await ctx.bot.send_message(channel, oneliner)

bot.run(config["discord"]["token"])
bot.loop.close()
