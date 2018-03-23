import discord, os, itertools
from discord.ext import commands
from utils import output, parsing, checks, mysql_module, g
import database

mysql = mysql_module.Mysql()
config = parsing.parse_json('config.json')["logging"]

class Server:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.is_owner)
    async def shutdown(self, ctx):
        """
        Shut down the bot [ADMIN ONLY]
        """
        author = str(ctx.message.author)
    
        try:
            await self.bot.say("Shutting down...")
            await self.bot.logout()
            self.bot.loop.stop()
            output.info('{} has shut down the bot...'.format(author))
    
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('{} has attempted to shut down the bot, but the following '
                         'exception occurred;\n\t->{}'.format(author, exc))

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.is_owner)
    async def restart(self, ctx):
        """
        Restart the bot [ADMIN ONLY]
        """
        author = str(ctx.message.author)
    
        try:
            await self.bot.say("Restarting...")
            await self.bot.logout()
            self.bot.loop.stop()
            output.info('{} has restarted the bot...'.format(author))
            os.system('sh restart.sh')
    
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('{} has attempted to restart the bot, but the following '
                         'exception occurred;\n\t->{}'.format(author, exc))

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.is_owner)
    async def load(self, ctx, module: str):
        """
        Load a cog located in /cogs [ADMIN ONLY]
        """
        author = str(ctx.message.author)
        module = module.strip()
    
        try:
            self.bot.load_extension("cogs.{}".format(module))
            output.info('{} loaded module: {}'.format(author, module))
            g.loaded_extensions.append(module)
            await self.bot.say("Successfully loaded {}.py".format(module))
    
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('{} attempted to load module \'{}\' but the following '
                         'exception occured;\n\t->{}'.format(author, module, exc))
            await self.bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))
    
    
    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.is_owner)
    async def unload(self, ctx, module: str):
        """
        Unload any loaded cog [ADMIN ONLY]
        """
        author = str(ctx.message.author)
        module = module.strip()
    
        try:
            self.bot.unload_extension("cogs.{}".format(module))
            output.info('{} unloaded module: {}'.format(author, module))
            g.startup_extensions.remove(module)
            await self.bot.say("Successfully unloaded {}.py".format(module))
    
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            await self.bot.say('Failed to load extension {}\n\t->{}'.format(module, exc))
    
    
    @commands.command(hidden=True)
    @commands.check(checks.is_owner)
    async def loaded(self):
        """
        List loaded cogs [ADMIN ONLY]
        """
        string = ""
        for cog in g.loaded_extensions:
            string += str(cog) + "\n"

        await self.bot.say('Currently loaded extensions:\n```{}```'.format(string))

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.in_server)
    @commands.check(checks.is_owner)
    async def allowsoak(self, ctx, enable: bool):
        """
        Enable and disable the soak feature [ADMIN ONLY]
        """
        mysql.set_soak(ctx.message.server, int(enable))
        if enable:
            await self.bot.say("Ok! Soaking is now enabled! :white_check_mark:")
        else:
            await self.bot.say("Ok! Soaking is now disabled! :no_entry_sign:")

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.is_owner)
    async def pull(self, ctx):
        """
        Update the bot [ADMIN ONLY]
        """
        await self.bot.say("Pulling...")
        try:
            returned = os.system("git pull")
            await self.bot.say(":+1:Returned code "+ str(returned))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('{} has attempted to update the bot, but the following '
                         'exception occurred;\n\t->{}'.format(ctx.message.author, exc))

    @commands.command(pass_context=True, hidden=True)
    @commands.check(checks.is_owner)
    async def log(self, ctx, num_lines: int):
        """
        Display the last couple lines of the log [ADMIN ONLY]
        """
        with open(config["file"], "r") as f:
            text = f.readlines()
        length = len(text)
        if num_lines < 1:
            num_lines = 5
        if num_lines > length:
            num_lines = length
        send = "```"
        for line in itertools.islice(text, length - num_lines, length):
            send += line
        send += "```"
        await self.bot.say(send)

def setup(bot):
    bot.add_cog(Server(bot))
