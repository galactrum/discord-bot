import discord, datetime, time
from discord.ext import commands

start_time = time.time()


class Uptime:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        current_time = time.time()
        difference = current_time - start_time
        text = str(datetime.timedelta(seconds=difference))
        await self.bot.say("Current uptime: " + text)


def setup(bot):
    bot.add_cog(Uptime(bot))
