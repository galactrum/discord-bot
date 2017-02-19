import discord, os, itertools
from discord.ext import commands
from utils import parsing, checks

config = parsing.parse_json('config.json')["logging"]


class Log:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.check(checks.is_owner)
    async def log(self, ctx, num_lines: int):
        with open(config["file"], "r") as f:
            text = f.readlines()
        length = len(text)
        send = ""
        for line in itertools.islice(text, length - num_lines, length):
            send += line

        await self.bot.say(send)


def setup(bot):
    bot.add_cog(Log(bot))
