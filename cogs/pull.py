import discord, os
from discord.ext import commands

class Pull:
    def init(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def pull(self, ctx):
        print("Pulling...")
        os.system("git pull")

def setup(bot):
    bot.add_cog(Pull(bot))