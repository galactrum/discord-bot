import discord, os
from discord.ext import commands
from utils import checks, output
from aiohttp import ClientSession
import urllib.request
import json

class Pricing:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def price(self, amount=1):
        """
        Checks the price of PHR
        """
        headers={"user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
        try:
            async with ClientSession() as session:
                async with session.get("https://coinsmarkets.com/apicoin.php", headers=headers) as response:
                    responseRaw = await response.read()
                    priceData = json.loads(responseRaw)['BTC_PHR']
                    embed = discord.Embed(colour=0x00FF00)
                    embed.add_field(name="24-hour Volume", value="{} BTC".format(priceData['24htrade']))
                    embed.add_field(name="24-hour Low", value="{} BTC".format(priceData['low24hr']))
                    embed.add_field(name="24-hour High", value="{} BTC".format(priceData['high24hr']))
                    embed.add_field(name="Price", value="{} PHR = {:.8f} BTC".format(amount, amount * float(priceData['last'])))
                    await self.bot.say(embed=embed)
        except:
            await self.bot.say(":warning: Error fetching prices!")


def setup(bot):
    bot.add_cog(Pricing(bot))
