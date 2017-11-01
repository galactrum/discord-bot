import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing
import math

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Withdraw:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def withdraw(self, ctx, address:str, amount:float):
        """Withdraw coins from your account to any Phore address"""
        snowflake = ctx.message.author.id
        name = ctx.message.author.name
        amount = abs(amount)
        
        if math.log10(amount) > 8:
            await self.bot.say(":warning:**Invalid amount!**:warning:")
            return

        mysql.check_for_user(name, snowflake)

        conf = rpc.validateaddress(address)
        if not conf["isvalid"]:
            await self.bot.say("{} **:warning:Invalid address!:warning:**".format(ctx.message.author.mention))
            return

        txid = rpc.sendfrom(snowflake, address, amount)

        await self.bot.say("{} **Withdrew {} PHR! :money_with_wings:**\nView the transaction here: https://chainz.cryptoid.info/phr/tx.dws?{}.htm".format(ctx.message.author.mention, str(amount), txid))

def setup(bot):
    bot.add_cog(Withdraw(bot))
