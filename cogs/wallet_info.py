import discord, json, requests
from discord.ext import commands
from utils import rpc_module as rpc


class Wallet:
    def __init__(self, bot):
        self.bot = bot
        self.rpc = rpc.Rpc()

    @commands.command()
    async def wallet(self):
        """Shows wallet info"""
        info = self.rpc.getinfo()
        wallet_balance = str(float(info["balance"]))
        block_height = info["blocks"]
        connection_count = self.rpc.getconnectioncount()
        embed = discord.Embed(colour=discord.Colour.red())
        embed.add_field(name="Balance", value="{:.8f} PHR".format(float(wallet_balance)))
        embed.add_field(name="Connections", value=connection_count)
        embed.add_field(name="Block Height", value=block_height)

        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("I need the `Embed links` permission to send this")


def setup(bot):
    bot.add_cog(Wallet(bot))

