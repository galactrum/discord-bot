import discord
from discord.ext import commands

class Test:
    @bot.command(pass_context=True)
    async def test(ctx):
        await self.bot.say(str(ctx.message.Message))


def setup(bot):
    bot.add_cog(Test(bot))
