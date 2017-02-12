import discord, json, requests, pymysql.cursors
from discord.ext import commands
from cogs.utils import rpc_module as rpc

#result_set = database response with parameters from query
#db_bal = nomenclature for result_set["balance"]
#author = author from message context, identical to user in database
#wallet_bal = nomenclature for wallet reponse

class Balance:

    def __init__(self, bot):
        self.bot = bot
        self.rpc = rpc.Rpc()

        #//Establish connection to db//
        self.connection = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            db='netcoin')
        self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)

    def make_user(self, author):
        #//If check_for_user() returns None, then INSERT new user info in db
        to_exec = """INSERT INTO db(user,balance)
        VALUES(%s,%s)"""
        self.cursor.execute(to_exec, (str(author), '0'))
        self.connection.commit()

    def check_for_user(self, author):
        #//Check if the user exists in the db by querying the db.
        #//If the db returns None, then the row does not exist
        try:
            to_exec = """SELECT user
            FROM db
            WHERE user
            LIKE %s"""
            self.cursor.execute(to_exec, (str(author)))
            result_set = self.cursor.fetchone()
            if result_set == None:
                self.make_user(author)
        except Exception as e:
            print("Error in SQL query: ",str(e))

    def update_db(self, author, db_bal, lasttxid):
        #//If user balance has been updated in parse_part... or parse_whole,
        #//update the db
        try:
            to_exec = """UPDATE db
            SET balance=%s, lasttxid=%s
            WHERE user
            LIKE %s"""
            self.cursor.execute(to_exec, (db_bal,lasttxid,str(author)))
            self.connection.commit()
        except Exception as e:
            print("Error: "+str(e))

    async def do_embed(self, author, db_bal):
        #//Simple embed function for displaying username and balance
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="User", value=author)
        embed.add_field(name="Balance (NET)", value="%.8f" % round(float(db_bal),8))
        embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    async def parse_part_bal(self,result_set,author):
        #//If user has a lasttxid value in the db, then stop parsing
        #//trans-list at a specific ["txid"] and submit
        #//changes to update_db
        params = author
        count = 1000
        get_transactions = self.rpc.listtransactions(params,count)
        i = len(get_transactions)-1

        new_balance = float(result_set["balance"])
        lasttxid = get_transactions[i]["txid"]
        if lasttxid == result_set["lasttxid"]:
            db_bal = result_set["balance"]
            await self.do_embed(author, db_bal)
        else:
            for tx in reversed(get_transactions):
                new_balance += float(tx["amount"])
                if tx["txid"] == result_set["lasttxid"]:
                    break
            db_bal = new_balance
            self.update_db(author, db_bal, lasttxid)
            await self.do_embed(author, db_bal)

    async def parse_whole_bal(self,result_set,author):
        #//If a user does not have a lasttxid in the db, the parse
        #//the entire trans-list for that user. Submit changes to
        #//update_db
        params = author
        user = params
        count = 1000
        get_transactions = self.rpc.listtransactions(params,count)
        i = len(get_transactions)-1

        if len(get_transactions) == 0:
            print("0 transactions found for "+author+", balance must be 0")
            db_bal = 0
            await self.do_embed(author, db_bal)
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
            await self.do_embed(author, db_bal)
            #Now update db with new balance

    @commands.command(pass_context=True)
    async def balance(self, ctx):
        #//Set important variables//
        author = str(ctx.message.author)

        #//Check if user exists in db
        self.check_for_user(author)


        #//Execute and return SQL Query
        try:
            to_exec = """
            SELECT balance, user, lasttxid, tipped
            FROM db
            WHERE user
            LIKE %s"""
            self.cursor.execute(to_exec, (str(author)))
            result_set = self.cursor.fetchone()
        except Exception as e:
            print("Error in SQL query: ",str(e))
            return
        #//
        if result_set["lasttxid"] == "0":
            await self.parse_whole_bal(result_set,author)
        else:
            await self.parse_part_bal(result_set,author)

def setup(bot):
    bot.add_cog(Balance(bot))
