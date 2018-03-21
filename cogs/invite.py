from discord.ext import commands


class Invite:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """
        Get the bot's invite link
        """
        channel_name = ctx.message.channel.name
        allowed_channel = parsing.parse_json('config.json')['command_channels'][ctx.command.name]
        if channel_name != allowed_channel:
            return

        await self.bot.say(":tada: https://discordapp.com/oauth2/authorize?permissions=0&client_id={}&scope=bot".format(self.bot.user.id))


def setup(bot):
    bot.add_cog(Invite(bot))
