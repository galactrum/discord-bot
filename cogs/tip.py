import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing

rpc = rpc_module.Rpc()
mysql = mysql_module.Mysql()


class Tip:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def tip(self, ctx, user:discord.Member, amount:float):
        """Tip a user coins"""
        snowflake = ctx.message.author.id
        name = ctx.message.author.name

        tip_user = user.id
        if snowflake == tip_user:
            await self.bot.say("{} **:warning:You cannot tip yourself!:warning:**".format(ctx.message.author.mention))
            return

        if amount <= 0.0:
            await self.bot.say("{} **:warning:You cannot tip <= 0!:warning:**".format(ctx.message.author.mention))
            return

        mysql.check_for_user(name, snowflake)

        result_set = mysql.get_user(snowflake)

        if float(result_set["balance"]) < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(ctx.message.author.mention))
        else:
            tip_user_address = rpc.getaccountaddress(tip_user)

            rpc.sendfrom(snowflake, tip_user_address, amount)
            await self.bot.say("{} **Tipped {} {} PHR! :money_with_wings:**".format(ctx.message.author.mention, user.mention, str(amount)))

def setup(bot):
    bot.add_cog(Tip(bot))
