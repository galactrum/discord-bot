import discord, json, requests
from discord.ext import commands
from utils import rpc_module
print(parsing.parse_json('config.json'))
rpc = rpc_module.Rpc()

class Deposit:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def deposit(self, ctx):
        """Shows wallet info"""
        account = ctx.message.author
        user_addy = rpc.getaccountaddress(str(account))
        await self.bot.say(account.mention + "'s Deposit Address: `" + str(user_addy) + "`")


def setup(bot):
    bot.add_cog(Deposit(bot))
