import discord
from discord.ext import commands


class Test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def test(self, ctx):
        await self.bot.say(":tada:{}:tada:".format(ctx.user.id))


def setup(bot):
    bot.add_cog(Test(bot))
