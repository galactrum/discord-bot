import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing
import decimal

rpc = rpc_module.Rpc()
Mysql = mysql_module.Mysql()


class Withdraw:
    def __init__(self, bot):
        self.bot = bot

    async def parse_part_bal(self,result_set,snowflake,name):
        # If user has a lasttxid value in the db, then stop parsing
        # trans-list at a specific ["txid"] and submit
        # changes to update_db
        count = 1000
        get_transactions = rpc.listtransactions(snowflake,count)
        i = len(get_transactions)-1

        new_balance = float(result_set["balance"])
        new_staked = float(result_set["staked"])
        lasttxid = get_transactions[i]["txid"]
        if lasttxid == result_set["lasttxid"]:
            db_bal = float(result_set["balance"])
            db_staked = float(result_set["staked"])
        else:
            for tx in reversed(get_transactions):
                if tx["txid"] == result_set["lasttxid"]:
                    break
                else:
                    new_balance += float(tx["amount"])
                    if "generated" in tx:
                        new_staked += float(tx["amount"])
                    else:
                        continue
            db_bal = new_balance
            db_staked = new_staked
            Mysql.update_db(snowflake, db_bal, db_staked, lasttxid)
            return snowflake, db_staked, db_bal
        # Updates balance
        # and return a tuple consisting of the snowflake, and their balance

    async def parse_whole_bal(self,snowflake,name):
        # If a user does not have a lasttxid in the db, the parse
        # the entire trans-list for that user. Submit changes to
        # update_db
        count = 1000
        get_transactions = rpc.listtransactions(snowflake,count)
        i = len(get_transactions)-1

        if len(get_transactions) == 0:
            db_bal = 0
            db_staked = 0
        else:
            new_balance = 0
            new_staked = 0
            lasttxid = get_transactions[i]["txid"]
            firsttxid = get_transactions[0]["txid"]
            while i <= len(get_transactions)-1:
                if get_transactions[i]["txid"] != firsttxid:
                    new_balance += float(get_transactions[i]["amount"])
                    if "generated" in get_transactions[i]:
                        new_staked += float(get_transactions[i]["amount"])
                    i -= 1
                else:
                    new_balance += float(get_transactions[i]["amount"])
                    if "generated" in get_transactions[i]:
                        new_staked += float(get_transactions[i]["amount"])
                    break
            db_bal = new_balance
            db_staked = new_staked
            Mysql.update_db(snowflake, db_bal, db_staked, lasttxid)
            return (snowflake, db_bal)

    @commands.command(pass_context=True)
    async def withdraw(self, ctx, address:str , amount:float):
        """Withdraw coins from your account to any Netcoin address"""
        snowflake = ctx.message.author.id
        name = ctx.message.author
        amount = abs(amount)
        
        if abs(decimal.Decimal(str(amount)).as_tuple().exponent) > 8:
            await self.bot.say(":warning:**Invalid amount!**:warning:")
            return
        to_send_to_user = amount- (amount / 100.0)
        to_send_to_bot = amount / 100.0

        Mysql.check_for_user(name, snowflake)

        result_set = Mysql.get_bal_lasttxid(snowflake)

        conf = rpc.validateaddress(address)
        if not conf["isvalid"]:
            await self.bot.say("{} **:warning:Invalid address!:warning:**".format(ctx.message.author.mention))
            return

        if result_set["lasttxid"] in ["0",""] or result_set["staked"] in ["0",""]:
            await self.parse_whole_bal(snowflake, name)
        else:
            await self.parse_part_bal(result_set, snowflake, name)

            rpc.sendfrom(snowflake, address, to_send_to_user)
            bot_addy = rpc.getaccountaddress(self.bot.user.id)
            rpc.sendfrom(snowflake, bot_addy, to_send_to_bot)
            await self.parse_part_bal(result_set, snowflake, name)
            await self.bot.say("{} **withdrew {} NET! :money_with_wings:**\n Fee: 1%, {} NET".format(name.mention, str(to_send_to_user),str(to_send_to_bot)))

def setup(bot):
    bot.add_cog(Withdraw(bot))
