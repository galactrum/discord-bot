import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module, parsing

rpc = rpc_module.Rpc()
Mysql = mysql_module.Mysql()


class Soak:
    def __init__(self, bot):
        self.bot = bot

    async def parse_part_bal(self,result_set,snowflake, name):
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
            Mysql.update_db(str(name), db_bal, lasttxid)
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
    async def soak(self, ctx, amount:float):
        """Tip all online users"""
        snowflake = ctx.message.author.id
        name = ctx.message.author
        
        online_users = [x for x in server.members if x.status == discord.Status.online]
        Mysql.check_for_user(name, snowflake)
        result_set = Mysql.get_bal_lasttxid(snowflake)

        if result_set["lasttxid"] == "0":
            user_bal = await self.parse_whole_bal(snowflake)
        else:
            user_bal = await self.parse_part_bal(result_set,snowflake,name)
           
        if float(result_set["balance"]) < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(name.mention))
            return
            
        for user in online_users:
            tip_user = user.id
            tip_user_addy = rpc.getaccountaddress(tip_user)

            rpc.sendfrom(snowflake, tip_user_addy, amount)
        
        await self.parse_part_bal(result_set, snowflake, name)
        await self.bot.say("{} **Soaked {} NET on {} [{}] :money_with_wings:**".format(
            name.mention,str(int(amount)/ len(online_users)), ', '.join[x.mention for x in online_users], str(amount))

def setup(bot):
bot.add_cog(Soak(bot))
