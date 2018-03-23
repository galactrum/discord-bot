import discord
from discord.ext import commands
from utils import output, parsing, checks, mysql_module, g
import os
import traceback
import database
import pdb

config = parsing.parse_json('config.json')

Mysql = mysql_module.Mysql()

bot = commands.Bot(command_prefix=config['prefix'], description=config["description"])

try:
    os.remove("log.txt")
except FileNotFoundError:
    pass

if "__pycache__" in g.startup_extensions:
    g.startup_extensions.remove("__pycache__")
g.startup_extensions = [ext.replace('.py', '') for ext in g.startup_extensions]

@bot.event
async def on_ready():
    output.info("Loading {} extension(s)...".format(len(g.startup_extensions)))

    for extension in g.startup_extensions:
        try:
            bot.load_extension("cogs.{}".format(extension.replace(".py", "")))
            g.loaded_extensions.append(extension)

        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('Failed to load extension {}\n\t->{}'.format(extension, exc))
    output.success('Successfully loaded the following extension(s): {}'.format(', '.join(g.loaded_extensions)))
    output.info('You can now invite the bot to a server using the following link: https://discordapp.com/oauth2/authorize?client_id={}&scope=bot'.format(bot.user.id))

@bot.event
async def on_server_join(server):
    output.info("Added to {0}".format(server.name))
    Mysql.add_server(server)
    for channel in server.channels:
        Mysql.add_channel(channel)

@bot.event
async def on_server_leave(server):
    Mysql.remove_server(server)
    output.info("Removed from {0}".format(server.name))

@bot.event
async def on_channel_create(channel):
    if isinstance(channel, discord.PrivateChannel):
        return
    Mysql.add_channel(channel)
    output.info("Channel {0} added to {1}".format(channel.name, channel.server.name))

@bot.event
async def on_channel_delete(channel):
    Mysql.remove_channel(channel)
    output.info("Channel {0} deleted from {1}".format(channel.name, channel.server.name))

@bot.event
async def on_command_error(error, ctx):
    channel = ctx.message.channel
    if isinstance(error, commands.MissingRequiredArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.BadArgument):
        await send_cmd_help(ctx)
    elif isinstance(error, commands.CommandInvokeError):
        output.error("Exception in command '{}', {}".format(ctx.command.qualified_name, error.original))
        oneliner = "Error in command '{}' - {}: {}\nIf this issue persists, Please report it in the support server.".format(
            ctx.command.qualified_name, type(error.original).__name__, str(error.original))
        await ctx.bot.send_message(channel, oneliner)

async def send_cmd_help(ctx):
    channel = ctx.message.channel
    allowed_channels = parsing.parse_json('config.json')['command_channels'][ctx.command.name]
    if channel.name not in allowed_channels:
        return

    if ctx.invoked_subcommand:
        pages = bot.formatter.format_help_for(ctx, ctx.invoked_subcommand)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)
    else:
        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            em = discord.Embed(title="Missing args :x:",
                               description=page.strip("```").replace('<', '[').replace('>', ']'),
                               color=discord.Color.red())
            await bot.send_message(ctx.message.channel, embed=em)


database.run()
bot.run(config["discord"]["token"])
bot.loop.close()
