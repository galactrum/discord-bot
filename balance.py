import discord, json, requests, pymysql.cursors
from discord.ext import commands

class balance:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def balance(self, ctx):
        author = ctx.message.author

        connection = pymysql.connect(host='localhost',
                                     user='root',
                                     password='',
                                     db='netcoin')
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""SELECT balance, user
                            FROM db
                            WHERE user
                            LIKE %s
                            """, str(author))
            result_set = cursor.fetchone()
            embed = discord.Embed(colour=discord.Colour.red())
            embed.add_field(name="User", value=result_set['user'])
            embed.add_field(name="Balance", value=result_set['balance'])
            embed.set_footer(text="Sponsored by altcointrain.com")

            try:
                await self.bot.say(embed=embed)
            except discord.HTTPException:
                await self.bot.say("I need the `Embed links` permission "
                                "to send this")

        except Exception as e:
            try:
                cursor.execute("""INSERT INTO db(user,balance) VALUES(%s,%s)""", (str(author), '0'))
                connection.commit()

                cursor.execute("""SELECT balance, user
                                FROM db
                                WHERE user
                                LIKE %s
                                """, str(author))
                result_set = cursor.fetchone()
                embed = discord.Embed(colour=discord.Colour.red())
                embed.add_field(name="User", value=result_set['user'])
                embed.add_field(name="Balance", value=result_set['balance'])
                embed.set_footer(text="Sponsored by altcointrain.com")

                try:
                    await self.bot.say(embed=embed)
                except discord.HTTPException:
                    await self.bot.say("I need the `Embed links` permission to send this")

            except Exception as ex:
                await self.bot.say("Error: "+str(ex))

def setup(bot):
    bot.add_cog(balance(bot))