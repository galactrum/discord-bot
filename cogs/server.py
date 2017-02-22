import discord, os, itertools
from discord.ext import commands
from utils import parsing, checks, mysql_module

Mysql = mysql_module.Mysql()


class Server:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_server_owner)
    async def allow_soak(self, ctx, enable: bool):
        Mysql.set_soak(ctx.message.server, int(enable))
        await self.bot.say("Ok!")


def setup(bot):
    bot.add_cog(Server(bot))
