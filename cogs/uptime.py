import discord, datetime, time
from discord.ext import commands
from utils import parsing

start_time = time.time()

class Uptime:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def uptime(self, ctx):
        """
        Get the time the bot has been active
        """
        channel_name = ctx.message.channel.name
        allowed_channel = parsing.parse_json('config.json')['command_channels'][ctx.command.name]
        if channel_name != allowed_channel:
            return

        current_time = time.time()
        difference = int(round(current_time - start_time))
        text = str(datetime.timedelta(seconds=difference))
        embed = discord.Embed(colour=0xFF0000)
        embed.add_field(name="Uptime", value=text)
        try:
            await self.bot.say(embed=embed)
        except discord.HTTPException:
            await self.bot.say("Current uptime: " + text)


def setup(bot):
    bot.add_cog(Uptime(bot))
