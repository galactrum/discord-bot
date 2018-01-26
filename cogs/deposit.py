import discord, json, requests
from discord.ext import commands
from utils import parsing, mysql_module

mysql = mysql_module.Mysql()

class Deposit:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def deposit(self, ctx):
        user = ctx.message.author
        # Check if user exists in db
        mysql.check_for_user(user.id)
        user_addy = mysql.get_address(user.id)
        await self.bot.send_message(user, user.mention + "'s Deposit Address: `" + str(user_addy) + "`" + "\n\nRemember to use !balance to check your balance and not an explorer. The address balance and your actual balance are not always the same!")
        if ctx.message.server is not None:
            await self.bot.say("{}, I PMed you your address! Make sure to double check that it is from me!".format(user.mention))

def setup(bot):
    bot.add_cog(Deposit(bot))
