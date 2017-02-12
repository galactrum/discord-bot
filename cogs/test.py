import discord
from discord.ext import commands


class Test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def test(self):
        await self.bot.say("Test!")

def setup(bot):
    bot.add_cog(Test(bot))