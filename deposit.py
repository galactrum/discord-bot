import discord, json, requests
from discord.ext import commands
from cogs.utils import rpc_module as rpc

rpc = rpc.Rpc

class deposit:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def deposit(self, ctx):
        """Shows wallet info"""
        port =  "11311"
        account = str(ctx.message.author)
        user_addy = rpc.getaddressesbyaccount(self, account)
        await self.bot.say(params.mention+"'s Deposit Address: `"+str(user_addy[0])+"`")

def setup(bot):
    bot.add_cog(deposit(bot))
