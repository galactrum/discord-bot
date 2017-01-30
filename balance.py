import discord, json, requests, pymysql.cursors
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
            print(user_wallet_bal)
            if float(db_bal) > float(user_wallet_bal) or float(db_bal) < float(user_wallet_bal):
                params = str(author)
                get_transactions = rpcdat('listtransactions',[params],port)
                top_index = get_transactions[-1]['blockindex']
                i = abs(top_index-int(result_set['lastblockindex']))
                new_balance = 0
                for h in range(i+1):
                    new_balance += float(get_transactions[h]['amount'])
                    h +=1
            try:
                cursor.execute("""
                                UPDATE db
                                SET balance=%s, lastblockindex=%s
                                WHERE user
                                LIKE %s
                                """, (new_balance, top_index, str(author)))
                connection.commit()
                self.new_balance = new_balance
            except Exception as e:
                print("48 Error: "+str(e))
            return
        self.update_balance = update_balance

    ###############################################################
    ###############EMBED BALANCE FOR DISPLAY IN CHAT###############
    async def embed_bal(self, user, db_bal):
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="User", value=user)
        embed.add_field(name="Balance (NET)", value=db_bal)
        embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")
        return

    ###############################################################
    ###################MAKE A NEW USER IN THE DB###################
    def make_new_user(self, author):
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
        self.embed_bal(user, db_bal)

    ###############################################################
    ########################BALANCE COMMAND########################
    @commands.command(pass_context=True)
    async def balance(self, ctx):
        port =  "11311"
        author = ctx.message.author
        params = str(author)
        user_wallet_bal = rpcdat('getbalance',[params],port)
        print(user_wallet_bal)

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='netcoin')
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("""SELECT balance, user, lastblockindex, tipped
                            FROM db
                            WHERE user
                            LIKE %s
                            """, str(author))
            result_set = cursor.fetchone()
            db_bal = result_set['balance']
            user = result_set['user']
            print(db_bal)
            if str(float(db_bal)) == str(user_wallet_bal):
                await self.embed_bal(user, db_bal)
            else:
                self.update_balance(result_set, db_bal, author)
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="User", value=user)
                embed.add_field(name="Balance (NET)", value=self.new_balance)
                embed.set_footer(text="Sponsored by altcointrain.com")
                try:
                    await self.bot.say(embed=embed)
                except discord.HTTPException:
                    await self.bot.say("I need the `Embed links` permission to send this")
        except Exception as e:
            try:
                print("127: "+str(e))
                self.make_new_user(author)
            except Exception as ex:
                print("130: "+str(ex))

def setup(bot):
    bot.add_cog(Balance(bot))
