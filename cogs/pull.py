import discord, os
from discord.ext import commands

class Pull:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def pull(self, ctx):
        await self.bot.say("Pulling...")
        returned = os.system("git pull")
        await self.bot.say(":+1:Returned code "+ returned)

def setup(bot):
    bot.add_cog(Pull(bot))
