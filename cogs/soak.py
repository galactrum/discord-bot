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

        new_balance = float(result_set["balance"])#set base balance; i.e. already processed transactions
        lasttxid = get_transactions[i]["txid"]    #set the very last txid to a var for storage for future checks
        if lasttxid == result_set["lasttxid"]:    #check if the last txid is equal to what we've already checked
            db_bal = float(result_set["balance"]) #in-case of True to 'if', our balance is correct     #output our balance
        else:                                     #in-case of False, our balance is incorrect, process new transactions
            for tx in reversed(get_transactions): #reverse the list so we can start from the beginning; i.e. end of transactions
                if tx["txid"] == result_set["lasttxid"]: #redundancy check for last txid
                    break                         #exit for statement if redundancy check is True
                else:                             #in-case of False (most cases), process new transactions
                    new_balance += float(tx["amount"]) #add new transactions to the new balance and loop again until 'if' is True
            db_bal = new_balance                  #make our balance equal our new balance for readability's sake
            Mysql.update_db(snowflake, db_bal, lasttxid) #update the database with the new info     #output our new balance

    async def parse_whole_bal(self,snowflake,name):
        # If a user does not have a lasttxid in the db, the parse
        # the entire trans-list for that user. Submit changes to
        # update_db
        count = 1000
        get_transactions = rpc.listtransactions(snowflake,count)
        i = len(get_transactions)-1

        if len(get_transactions) == 0:
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
            #Now update db with new balance

    @commands.command(pass_context=True)
    async def soak(self, ctx, amount: float):
        """Tip all online users"""
        snowflake = ctx.message.author.id
        name = ctx.message.author
        
        online_users = [x for x in ctx.message.server.members if x.status == discord.Status.online]
        online_users.remove(name)
        online_users.remove(ctx.message.server.me)
        Mysql.check_for_user(name, snowflake)
        result_set = Mysql.get_bal_lasttxid(snowflake)

        if result_set["lasttxid"] in ["0",""]:
            await self.parse_whole_bal(snowflake, name)
        else:
            await self.parse_part_bal(result_set, snowflake,name)
           
        if float(result_set["balance"]) < amount:
            await self.bot.say("{} **:warning:You cannot tip more money than you have!:warning:**".format(name.mention))
            return

        amount_split = int(amount) / len(online_users)

        for user in online_users:
            Mysql.check_for_user(user, user.id)
            address = rpc.getaccountaddress(user.id)
            rpc.sendfrom(snowflake, address, amount_split)
        
        await self.parse_part_bal(result_set, snowflake, name)
        await self.bot.say("{} **Soaked {} NET on {} [{}] :money_with_wings:**".format(
            name.mention, str(amount_split), ', '.join([x.mention for x in online_users]), str(amount)))


def setup(bot):
    bot.add_cog(Soak(bot))
