import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing

rpc = rpc_module.Rpc()
Mysql = mysql_module.Mysql()


class Withdraw:
    def __init__(self, bot):
        self.bot = bot

    async def parse_part_bal(self,result_set,snowflake):
        params = snowflake
        count = 1000
        get_transactions = rpc.listtransactions(params,count)
        i = len(get_transactions)-1

        new_balance = float(result_set["balance"])
        lasttxid = get_transactions[i]["txid"]
        if lasttxid == result_set["lasttxid"]:
            db_bal = result_set["balance"]
            return
        else:
            while i <= len(get_transactions):
                if get_transactions[i]["txid"] != result_set["lasttxid"]:
                    new_balance += float(get_transactions[i]["amount"])
                    i -= 1
                else:
                    new_balance += float(get_transactions[i]["amount"])
                    break
            db_bal = new_balance
            Mysql.update_db(name, db_bal, lasttxid)
            return snowflake, db_bal
        # Updates balance
        # and return a tuple consisting of the snowflake, and their balance

    async def parse_whole_bal(self,snowflake):
        count = 1000
        get_transactions = rpc.listtransactions(snowflake,count)
        i = len(get_transactions)-1

        if len(get_transactions) == 0:
            print("0 transactions found for "+snowflake+", balance must be 0")
            db_bal = 0
        else:
            new_balance = 0
            lasttxid = get_transactions[i]["txid"]
            firsttxid = get_transactions[0]["txid"]
            while i <= len(get_transactions)-1:
                if get_transactions[i]["txid"] != firsttxid:
                    new_balance += float(get_transactions[i]["amount"])
                    i -= 1
                else:
                    new_balance += float(get_transactions[i]["amount"])
                    break
            db_bal = new_balance
            Mysql.update_db(snowflake, db_bal, lasttxid)
            return (snowflake, db_bal)

    @commands.command(pass_context=True)
    async def withdraw(self, ctx, address:str , amount:float):
        """Withdraw coins from your account to any Netcoin address"""
        snowflake = ctx.message.author.id
        name = ctx.message.author

        to_send_to_user = amount-((1 * amount) / 100.0)
        to_send_to_bot = (1 * amount) / 100.0

        Mysql.check_for_user(name, snowflake)

        result_set = Mysql.get_bal_lasttxid(snowflake)

        if result_set["lasttxid"] == "0":
            user_bal = await self.parse_whole_bal(snowflake)
        else:
            user_bal = await self.parse_part_bal(result_set,snowflake)

        if float(result_set["balance"]) < amount:
            await self.bot.say("{} **:warning:You cannot withdraw more money than you have!:warning:**".format(name.mention))
        else:
            conf = rpc.validateaddress(address)
            if not conf["isvalid"]:
                await self.bot.say("{} **:warning:Invalid address!:warning:**".format(name.mention))
                return

            rpc.sendfrom(snowflake, address, to_send_to_user)
            bot_addy = rpc.getaccountaddress(self.bot.user.id)
            rpc.sendfrom(snowflake, bot_addy, to_send_to_bot)
            await self.parse_part_bal(result_set, snowflake)
            await self.bot.say("{} **withdrew {} NET! :money_with_wings:**".format(name.mention, str(to_send_to_user)))

def setup(bot):
    bot.add_cog(Withdraw(bot))
