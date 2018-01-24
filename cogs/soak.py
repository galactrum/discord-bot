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
        if ctx.message.author in online_users:
            online_users.remove(ctx.message.author)
        for user in online_users:
            if user.bot:
                online_users.remove(user)

        if len(online_users) == 0:
            await self.bot.say("{}, you are all alone if you don't include bots! Trying soaking when people are online.".format(ctx.message.author.mention))
            return

        mysql.check_for_user(name, snowflake)
        balance = mysql.get_balance(snowflake, check_update=True)

        if float(balance) < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(ctx.message.author.mention))
            return

        amount_split = math.floor(float(amount) * 1e8 / len(online_users)) / 1e8

        for user in online_users:
            mysql.check_for_user(user.name, user.id)
            mysql.add_tip(snowflake, user.id, amount_split)

        await self.bot.say("{} **Soaked {} PHR on {} [{}] :money_with_wings:**".format(ctx.message.author.mention, str(amount_split), ', '.join([x.mention for x in online_users]), str(amount)))


def setup(bot):
    bot.add_cog(Soak(bot))
