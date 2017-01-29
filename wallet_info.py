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

class wallet_info:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wallet(self):
        """Shows wallet info"""
        port =  "11311"
        wallet_balance = rpcdat('getbalance',[],port)
        stake_info = rpcdat('getstakinginfo',[],port)
        stake_weight = stake_info["weight"]
        net_weight = stake_info["netstakeweight"]
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Wallet owner", value="Aareon")
        embed.add_field(name="Balance", value=wallet_balance)
        embed.add_field(name="Staking Weight", value=stake_weight)
        embed.add_field(name="Net Stake Weight", value=net_weight)

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

def setup(bot):
    bot.add_cog(wallet_info(bot))