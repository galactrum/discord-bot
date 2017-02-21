import discord
from discord.ext import commands


class Help:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def help(self, ctx):
        for key in self.bot.commands.keys():
            command = self.bot.get_command(key)
            if command.aliases and not command.hidden:
                desc += "`!{}`".format(command.name)+" - {}\nAliases: `{}`\n".format(command.short_doc,
                ",".join(command.aliases))
                
                desc += "\n"
                
                elif


def setup(bot):
    bot.add_cog(Help(bot))
