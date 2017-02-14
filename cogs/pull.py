import discord, os
from discord.ext import commands
from utils import checks

class Pull:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_owner)
    async def pull(self, ctx):
        await self.bot.say("Pulling...")
        try:
            returned = os.system("git pull")
            await self.bot.say(":+1:Returned code "+ str(returned))
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            output.error('{} has attempted to update the bot, but the following '
                         'exception occurred;\n\t->{}'.format(author, exc))


def setup(bot):
    bot.add_cog(Pull(bot))
