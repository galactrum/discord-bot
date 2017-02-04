import discord, json, requests, pymysql.cursors
from itertools import takewhile
from discord.ext import commands

def rpcdat(method,params,port):
    try:
        rpcdata = json.dumps({
            "jsonrpc": 1.0,
            "id":"rpctest",
            "method": str(method),
            "params": params,
            "port": port
            })
        req = requests.get('http://127.0.0.1:'+port, data=rpcdata, auth=('srf2UUR0', 'srf2UUR0XomxYkWw'), timeout=8)
        return req.json()['result']
    except Exception as e:
        return "Error: "+str(e)

class Balance:

    def __init__(self, bot):
        self.bot = bot

    ###############################################################
    ##UPDATE BALANCE IN DB BASED ON TRANSACTIONS AFTER BLOCKINDEX##
        def update_balance(result_set, db_bal, author):

            connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='netcoin')
            cursor = connection.cursor(pymysql.cursors.DictCursor)

            port =  "11311"
            params = str(author)
            user_wallet_bal = rpcdat('getbalance',[params],port)
            if float(db_bal) > float(user_wallet_bal) or float(db_bal) < float(user_wallet_bal):
                params = str(author)
                get_transactions = rpcdat('listtransactions',[params],port)
                new_balance = 0

                i = len(get_transactions)-1
                if len(get_transactions) == 0:
                    print("0 transactions found for %s, balance must be 0", author)
                    return
                lastblockhash = get_transactions[i]["blockhash"]
                while i <= len(get_transactions)-1:
                    if get_transactions[i]["blockhash"] != result_set["lastblockhash"]:
                        self.new_balance += float(get_transactions[i]["amount"])
                        i -= 1
                    else:
                        self.new_balance += float(get_transactions[i]["amount"])
                        break
                try:
                    cursor.execute("""
                        UPDATE db
                        SET balance=%s, lastblockhash=%s
                        WHERE user
                        LIKE %s
                        """, (new_balance, lastblockhash, str(author)))
                    connection.commit()
                except Exception as e:
                    print("48 Error: "+str(e))
                return
            self.new_balance = new_balance
        self.update_balance = update_balance

    ###############################################################
    ###############EMBED BALANCE FOR DISPLAY IN CHAT###############
    async def embed_bal(self, author, db_bal):
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="User", value=author)
        embed.add_field(name="Balance (NET)", value="%.8f" % round(float(db_bal),8))
        embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")
        return

    ###############################################################
    ###################MAKE A NEW USER IN THE DB###################
    async def make_new_user(self, author):
        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='netcoin')
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute("""INSERT INTO db(user,balance) VALUES(%s,%s)""", (str(author), '0'))
        connection.commit()

        cursor.execute("""SELECT balance, user
                        FROM db
                        WHERE user
                        LIKE %s
                        """, str(author))
        result_set = cursor.fetchone()
        db_bal = result_set["balance"]

        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="User", value=author)
        embed.add_field(name="Balance (NET)", value="%.8f" % round(float(db_bal),8))
        embed.set_footer(text="Sponsored by altcointrain.com")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

    ###############################################################
    ########################BALANCE COMMAND########################
    @commands.command(pass_context=True)
    async def balance(self, ctx):
        port =  "11311"
        author = ctx.message.author
        params = str(author)
        user_wallet_bal = rpcdat('getbalance',[params],port)

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='netcoin')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("""SELECT balance, user, lastblockhash, tipped
                            FROM db
                            WHERE user
                            LIKE %s
                            """, str(author))
            result_set = cursor.fetchone()
            db_bal = result_set['balance']
            user = result_set['user']
            if str(float(db_bal)) == str(user_wallet_bal):
                await self.embed_bal(author, db_bal)
            else:
                self.update_balance(result_set, db_bal, author)
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="User", value=author)
                embed.add_field(name="Balance (NET)", value="%.8f" % round(float(self.new_balance),8))
                embed.set_footer(text="Sponsored by altcointrain.com")
                try:
                    await self.bot.say(embed=embed)
                except discord.HTTPException:
                    await self.bot.say("I need the `Embed links` permission to send this")
        except Exception as e:
            try:
                print("127: "+str(e))
                await self.make_new_user(author)
            except Exception as ex:
                print("130: "+str(ex))

def setup(bot):
    bot.add_cog(Balance(bot))
