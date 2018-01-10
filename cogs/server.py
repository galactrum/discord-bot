import discord, os, itertools
from discord.ext import commands
from utils import parsing, checks, mysql_module

mysql = mysql_module.Mysql()


class Server:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.in_server)
    @commands.check(checks.is_owner)
    async def allowsoak(self, ctx, enable: bool):
        """
        Should the users in the server be allowed to soak all online users?
        """
        mysql.set_soak(ctx.message.server, int(enable))
        if enable:
            await self.bot.say("Ok! Soaking is now enabled!")
        else:
            await self.bot.say("Ok! Soaking is now disabled.")

    @commands.command(pass_context=True)
    @commands.check(checks.in_server)
    @commands.check(checks.is_owner)
    async def checksoak(self, ctx):
        """
        Checks if soak is available on the server.
        """
        result_set = mysql.check_soak(ctx.message.server)
        if result_set:
            await self.bot.say("Soaking is enabled!")
        else:
            await self.bot.say("Soaking is disabled.")


def setup(bot):
    bot.add_cog(Server(bot))
