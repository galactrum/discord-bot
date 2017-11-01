import math
import discord
from discord.ext import commands
from utils import rpc_module, mysql_module, checks

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Soak:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.allow_soak)
    async def soak(self, ctx, amount: float):
        """Tip all online users"""
        snowflake = ctx.message.author.id
        name = ctx.message.author.name

        online_users = [x for x in ctx.message.server.members if x.status == discord.Status.online]
        online_users.remove(ctx.message.author)
        for user in online_users:
            if user.bot:
                online_users.remove(user)

        mysql.check_for_user(name, snowflake)
        result_set = mysql.get_user(snowflake)

        if float(result_set["balance"]) < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(ctx.message.author.mention))
            return

        amount_split = math.floor(float(amount) * 1e8 / len(online_users)) / 1e8

        payments = {}
        for user in online_users:
            address = rpc.getaccountaddress(user.id)
            payments[address] = amount_split
        rpc.sendmany(snowflake, payments)

        await self.bot.say("{} **Soaked {} PHR on {} [{}] :money_with_wings:**".format(ctx.message.author.mention, str(amount_split), ', '.join([x.mention for x in online_users]), str(amount)))


def setup(bot):
    bot.add_cog(Soak(bot))
