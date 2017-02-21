import discord
from discord.ext import commands
from utils import rpc_module, mysql_module

#result_set = database response with parameters from query
#db_bal = nomenclature for result_set["balance"]
#snowflake = snowflake from message context, identical to user in database
#wallet_bal = nomenclature for wallet reponse

rpc = rpc_module.Rpc()
Mysql = mysql_module.Mysql()


class Balance:

    def __init__(self, bot):
        self.bot = bot

    async def do_embed(self, name, db_bal, db_staked):
        # Simple embed function for displaying username and balance
        embed = discord.Embed(colour=name.top_role.colour)
        embed.add_field(name="User", value=name.mention)
        embed.add_field(name="Balance (NET)", value="%.8f" % round(float(db_bal),8))
        embed.add_field(name="Staked", value="%.8f" % round(float(db_staked), 8))
        embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")

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
            await self.do_embed(name, db_bal, db_staked)
        else:
            for tx in reversed(get_transactions):
                if tx["txid"] == result_set["lasttxid"]:
                    break
                else:
                    new_balance += float(tx["amount"])
                    if tx["category"] == "generate":
                        new_staked += float(tx["amount"])
            db_bal = new_balance
            db_staked = new_staked
            Mysql.update_db(snowflake, db_bal, db_staked, lasttxid)
            await self.do_embed(name, db_bal, db_staked)

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
            await self.do_embed(name, db_bal, db_staked)
        else:
            new_balance = 0
            new_staked = 0
            lasttxid = get_transactions[i]["txid"]
            firsttxid = get_transactions[0]["txid"]
            while i <= len(get_transactions)-1:
                if get_transactions[i]["txid"] != firsttxid:
                    new_balance += float(get_transactions[i]["amount"])
                    if get_transactions[i]["category"] == "generate":
                        new_staked += float(get_transactions[i]["amount"])
                    i -= 1
                else:
                    new_balance += float(get_transactions[i]["amount"])
                    if get_transactions[i]["category"] == "generate":
                        new_staked += float(get_transactions[i]["amount"])
                    break
            db_bal = new_balance
            db_staked = new_staked
            Mysql.update_db(snowflake, db_bal, db_staked, lasttxid)
            await self.do_embed(name, db_bal, db_staked)
            #Now update db with new balance

    @commands.command(pass_context=True)
    async def balance(self, ctx):
        """Display your balance"""
        # Set important variables
        snowflake = ctx.message.author.id
        name = ctx.message.author

        # Check if user exists in db
        result_set = Mysql.check_for_user(name, snowflake)


        # Execute and return SQL Query
        result_set = Mysql.get_user(snowflake)

        if result_set["lasttxid"] in ["0",""] or result_set["staked"] in ["0",""]:
            await self.parse_whole_bal(snowflake, name)
        else:
            await self.parse_part_bal(result_set, snowflake, name)


def setup(bot):
    bot.add_cog(Balance(bot))
