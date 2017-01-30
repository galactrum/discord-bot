import discord, json, requests
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

class wallet:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def wallet(self):
        """Shows wallet info"""
        port =  "11311"
        get_info = rpcdat('getinfo',[],port)
        wallet_balance = float(get_info["balance"])+float(get_info["stake"])
        stake_info = rpcdat('getstakinginfo',[],port)
        connection_count = rpcdat('getconnectioncount',[],port)
        stake_weight = stake_info["weight"]
        net_weight = stake_info["netstakeweight"]
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Wallet owner", value="Aareon#0892")
        embed.add_field(name="Balance (NET)", value=wallet_balance)
        embed.add_field(name="Staking Weight", value=stake_weight)
        embed.add_field(name="Net Stake Weight", value=net_weight)
        embed.add_field(name="Connections", value=connection_count)
        embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

def setup(bot):
    bot.add_cog(wallet(bot))
