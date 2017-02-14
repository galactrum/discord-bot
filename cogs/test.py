import discord
from discord.ext import commands


@commands.command(pass_context=True)
async def test(self, ctx):
    await self.bot.say(str(ctx.message.Message))


def setup(bot):
    bot.add_cog(test(bot))
