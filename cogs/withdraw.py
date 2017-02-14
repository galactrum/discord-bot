import discord, json, requests, pymysql.cursors
from discord.ext import commands
from utils import rpc_module, mysql_module

rpc = rpc_module.Rpc()
connector = mysql_module.Mysql()
connection = connector.connect()
cursor = connector.cursor()


class Withdraw:
    def __init__(self, bot):
        self.bot = bot

    def make_user(self, author):
        to_exec = "INSERT INTO person(user,balance) VALUES(%s,%s)"
        cursor.execute(to_exec, str(author), '0')
        connection.commit()
        return

    def update_db(self, author, db_bal, lasttxid):
        # If user balance has been updated in parse_part... or parse_whole,
        # update the db
        try:
            to_exec = """UPDATE db
            SET balance=%s, lasttxid=%s
            WHERE user
            LIKE %s"""
            cursor.execute(to_exec, (db_bal,lasttxid,str(author)))
            connection.commit()
        except Exception as e:
            print("Error: "+str(e))

    def check_for_user(self, author):
        try:
            to_exec = """
                    SELECT user
                    FROM db
                    WHERE user
                    LIKE %s
                    """
            cursor.execute(to_exec, str(author))
            result_set = cursor.fetchone()
        except Exception as e:
            print("Error in SQL query: ",str(e))
            return
        if result_set == None:
            self.make_user(author)
            return

    async def parse_part_bal(self,result_set,author):
        params = author
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
            self.update_db(author, db_bal, lasttxid)
            return (author, db_bal)
        # Updates balance
        # and return a tuple consisting of the author, and their balance

    async def parse_whole_bal(self,result_set,author):
        params = author
        user = params
        count = 1000
        get_transactions = rpc.listtransactions(params,count)
        i = len(get_transactions)-1

        if len(get_transactions) == 0:
            print("0 transactions found for "+author+", balance must be 0")
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
            self.update_db(author, db_bal, lasttxid)
            return (author, db_bal)
            #Now update db with new balance
            # and return a tuple consisting of the author, and their balance

    @commands.command(pass_context=True)
    async def withdraw(self, ctx, address:str , amount:float):
        """Withdraw coins from your account to any Netcoin address"""
        port =  "11311"

        author_name = str(ctx.message.author)

        self.check_for_user(author_name)

        #user_addy = rpcdat('getaddressesbyaccount',[author_name],port)
        #deposite_addr = user_addy[0]

        to_exec = " SELECT balance,lasttxid FROM db WHERE user LIKE %s "
        user_bal = 0.0

        cursor.execute(to_exec,(author_name))
        result_set = cursor.fetchone()

        if result_set["lasttxid"] == "0":
            user_bal = await self.parse_whole_bal(result_set,author_name)
        else:
            user_bal = await self.parse_part_bal(result_set,author_name)

        cursor.execute(to_exec,(author_name))
        result_set = cursor.fetchone()

        if float(result_set["balance"]) < amount:
            await self.bot.say("**:warning:You cannot withdraw more money than you have!:warning:**")
        else:
            conf = rpc.validateaddress(address)
            if not conf["isvalid"]:
                await self.bot.say("**:warning:Invalid address!:warning:**")
                return

            rpc.withdraw(author_name, address, amount)
            await self.parse_part_bal(result_set, author_name)
            await self.bot.say("**Withdrew {} NET! :money_with_wings:**".format(str(amount)))

        # removes `message` amount from `wallet` and adds `message` amount to `address` provided
                    
"""		
        try:
            if user_addy[0] == "":
                new_user_addy = rpcdat('',)
            else:

        except IndexError:
            await self.bot.say("You don't have an account.")
"""


def setup(bot):
    bot.add_cog(Withdraw(bot))
