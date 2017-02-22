import discord, os, itertools
from discord.ext import commands
from utils import parsing, checks

import database


class DB:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_owner)
    async def configure_the_database(self, ctx):
        database.run()
        await self.bot.say("Ok!")


def setup(bot):
    bot.add_cog(DB(bot))
