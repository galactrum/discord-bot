import discord, os
from discord.ext import commands
from utils import checks, output
from aiohttp import ClientSession
import urllib.request
import json

class Stats:
    def __init__(self, bot: discord.ext.commands.Bot):
        self.bot = bot

    @commands.command()
    async def stats(self, amount=1):
        """
        Show stats about ORE
        """
        headers={"user-agent" : "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.78 Safari/537.36"}
        try:
            async with ClientSession() as session:
                async with session.get("https://api.coinmarketcap.com/v1/ticker/galactrum/", headers=headers) as response:
                    responseRaw = await response.read()
                    priceData = json.loads(responseRaw)
                    for item in priceData:
                        embed= discord.Embed(colour=0x00FF00)
                        embed.set_author(name='ORE Information', icon_url="https://explorer.galactrum.org/images/logo.png")
                        embed.add_field(name="Price (USD)", value="${}".format(item['price_usd']))
                        embed.add_field(name="Price (BTC)", value="{} BTC".format(item['price_btc']))
                        embed.add_field(name='\u200b',value='\u200b')
                        embed.add_field(name="Volume (USD)", value="${}".format(item['24h_volume_usd']))
                        embed.add_field(name="Market Cap", value="${}".format(item['market_cap_usd']))
                        embed.add_field(name='\u200b',value='\u200b')
                        embed.add_field(name="% 1h", value="{}%".format(item['percent_change_1h']))
                        embed.add_field(name="% 24h", value="{}%".format(item['percent_change_24h']))
                        embed.add_field(name="% 7d", value="{}%".format(item['percent_change_7d']))
                        embed.add_field(name="Circulating Supply", value="{} ORE".format(item['available_supply']))
                        embed.add_field(name="Total Supply", value="{} ORE".format(item['total_supply']))
                        embed.add_field(name="Maximum Supply", value="26,280,000 ORE")
                        embed.set_footer(text="https://coinmarketcap.com/currencies/galactrum/", icon_url="https://explorer.galactrum.org/images/logo.png")
                    await self.bot.say(embed=embed)
        except:
            await self.bot.say(":warning: Error fetching prices!")


def setup(bot):
    bot.add_cog(Stats(bot))
