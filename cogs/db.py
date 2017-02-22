import discord, os, itertools
from discord.ext import commands
from utils import parsing, checks, mysql_module

import database

Mysql = mysql_module.Mysql()


class DB:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_owner)
    async def configure_the_database(self, ctx):
        database.run()
        await self.bot.say("Ok!")

    @commands.command(pass_context=True)
    @commands.check(checks.is_owner)
    async def check_soak(self, ctx):
        result_set = Mysql.check_soak(ctx.message.server)
        await self.bot.say(result_set)


def setup(bot):
    bot.add_cog(DB(bot))
