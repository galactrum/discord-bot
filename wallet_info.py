import discord, json, requests
from discord.ext import commands
from cogs.utils import rpc_module as rpc

class wallet:
    def __init__(self, bot):
        self.bot = bot
        self.rpc = rpc.Rpc()

    @commands.command()
    async def wallet(self):
        """Shows wallet info"""
        get_info = self.rpc.getinfo()
        wallet_balance = float(get_info["balance"])+float(get_info["stake"])
        block_height = get_info["blocks"]
        stake_info = self.rpc.getstakinginfo()
        connection_count = self.rpc.getconnectioncount()
        stake_weight = stake_info["weight"]
        net_weight = stake_info["netstakeweight"]
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Wallet owner", value="Aareon#0892")
        embed.add_field(name="Balance (NET)", value=wallet_balance)
        embed.add_field(name="Staking Weight", value=stake_weight)
        embed.add_field(name="Net Stake Weight", value=net_weight)
        embed.add_field(name="Connections", value=connection_count)
        embed.add_field(name="Block Height", value=connection_count)
        embed.set_footer(text="Sponsored by altcointrain.com - Choo!!! Choo!!!")

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission "
                               "to send this")

def setup(bot):
    bot.add_cog(wallet(bot))
