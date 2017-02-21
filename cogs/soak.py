import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing

rpc = rpc_module.Rpc()
Mysql = mysql_module.Mysql()


class Soak:
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
            db_bal = new_balance
            db_staked = new_staked
            Mysql.update_db(snowflake, db_bal, db_staked, lasttxid)

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
            #Now update db with new balance

    @commands.command(pass_context=True)
    async def soak(self, ctx, amount: float):
        """Tip all online users"""
        snowflake = ctx.message.author.id
        name = ctx.message.author
        
        online_users = [x for x in ctx.message.server.members if x.status == discord.Status.online]
        online_users.remove(name)
        for user in online_users:
            if user.bot == True:
                online_users.remove(user)
        Mysql.check_for_user(name, snowflake)
        result_set = Mysql.get_bal_lasttxid(snowflake)

        if result_set["lasttxid"] in ["0",""] or result_set["staked"] in ["0",""]:
            await self.parse_whole_bal(snowflake, name)
        else:
            await self.parse_part_bal(result_set, snowflake, name)
           
        if float(result_set["balance"]) < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(name.mention))
            return

        amount_split = round(float(amount) / len(online_users), 8)

        payments = {}
        for user in online_users:
            address = rpc.getaccountaddress(user.id)
            payments[address] = amount_split
        rpc.sendmany(snowflake, payments)
        
        await self.parse_part_bal(result_set, snowflake, name)
        await self.bot.say("{} **Soaked {} NET on {} [{}] :money_with_wings:**".format(
            name.mention, str(amount_split), ', '.join([x.mention for x in online_users]), str(amount)))


def setup(bot):
    bot.add_cog(Soak(bot))
