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
		req = requests.get('http://127.0.0.1:'+port, data=rpcdata, auth=('user', 'pass'), timeout=8)
		return req.json()['result']
	except Exception as e:
		return "Error: "+str(e)

class deposit:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True)
	async def deposit(self, ctx):
		"""Shows wallet info"""
		port =  "11311"
		params = ctx.message.author
		user_addy = rpcdat('getaddressesbyaccount',[str(params)],port)
		try:
			if user_addy[0] == "":
				new_user_addy = rpcdat('',)
			else:
				await self.bot.say(params.mention+"'s Deposit Address: `"+str(user_addy[0])+"`")
		except IndexError:
			user_addy = rpcdat('getaccountaddress',[str(params)],port)
			await self.bot.say(params.mention+"'s Deposit Address: `"+str(user_addy[0])+"`")

def setup(bot):
	bot.add_cog(deposit(bot))
