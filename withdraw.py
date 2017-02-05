import discord, json, requests, pymysql.cursors
from discord.ext import commands

class rpc:

	def __init__(self):
		self.port = "11311"
		self.rpc_user = 'srf2UUR0'
		self.rpc_pass = 'srf2UUR0XomxYkWw'
		self.serverURL = 'http://localhost:'+self.port
		self.headers = {'content-type': 'application/json'}

	def listtransactions(self,params,count):
		payload = json.dumps({"method": "listtransactions", "params": [params,count], "jsonrpc": "2.0"})
		response = requests.get(self.serverURL, headers=self.headers, data=payload, auth=(self.rpc_user,self.rpc_pass))
		return(response.json()['result'])

	def validateaddress(self,params):
		payload = json.dumps({"method": "validateaddress", "params": [params], "jsonrpc": "2.0"})
		response = requests.get(self.serverURL, headers=self.headers, data=payload, auth=(self.rpc_user,self.rpc_pass))
		return(response.json()['result'])
	
	def withdraw(self,account, address, amount):
		payload = json.dumps({"method": "sendfrom", "params": [account,address, amount], "jsonrpc": "2.0"})
		response = requests.get(self.serverURL, headers=self.headers, data=payload, auth=(self.rpc_user,self.rpc_pass))
		return(response.json()['result'])

class withdraw:
	def __init__(self, bot):
		self.bot = bot

		self.connection = pymysql.connect(
			host='localhost',
			user='root',
			password='',
			db='netcoin')
		self.cursor = self.connection.cursor(pymysql.cursors.DictCursor)
		self.rpc = rpc()

	def make_user(self, author):
		print(author)
		to_exec = """
				INSERT INTO db(user,balance)
				VALUES(%s,%s)
				"""
		self.cursor.execute(to_exec, str(author), '0')
		self.connection.commit()
		return

	def check_for_user(self, author):
		try:
			to_exec = """
					SELECT user
					FROM db
					WHERE user
					LIKE %s
					"""
			self.cursor.execute(to_exec, str(author))
			result_set = self.cursor.fetchone()
		except Exception as e:
			print("Error in SQL query: ",str(e))
			return
		if result_set == None:
			self.make_user(author)
			return

	async def parse_part_bal(self,result_set,author):
		params = author
		count = 1000
		get_transactions = self.rpc.listtransactions(params,count)
		print(len(get_transactions))
		i = len(get_transactions)-1

		new_balance = float(result_set["balance"])
		lastblockhash = get_transactions[i]["blockhash"]
		print("LBH: ",lastblockhash)
		if lastblockhash == result_set["lastblockhash"]:
			db_bal = result_set["balance"]
			return
		else:
			while i <= len(get_transactions):
				if get_transactions[i]["blockhash"] != result_set["lastblockhash"]:
					new_balance += float(get_transactions[i]["amount"])
					i -= 1
				else:
					new_balance += float(get_transactions[i]["amount"])
					break
			db_bal = new_balance
			self.update_db(author, db_bal, lastblockhash)
			return (author, db_bal)
		# Updates balance
		# and return a tuple consisting of the author, and their balance

	async def parse_whole_bal(self,result_set,author):
		params = author
		user = params
		count = 1000
		get_transactions = self.rpc.listtransactions(params,count)
		print(len(get_transactions))
		i = len(get_transactions)-1

		if len(get_transactions) == 0:
			print("0 transactions found for "+author+", balance must be 0")
			db_bal = 0
		else:
			new_balance = 0
			lastblockhash = get_transactions[i]["blockhash"]
			firstblockhash = get_transactions[0]["blockhash"]
			print("FBH: ",firstblockhash)
			print("LBH: ",lastblockhash)
			while i <= len(get_transactions)-1:
				if get_transactions[i]["blockhash"] != firstblockhash:
					new_balance += float(get_transactions[i]["amount"])
					i -= 1
					print("New Balance: ",new_balance)
				else:
					new_balance += float(get_transactions[i]["amount"])
					print("New Balance: ",new_balance)
					break
			db_bal = new_balance
			self.update_db(author, db_bal, lastblockhash)
			return (author, db_bal)
			#Now update db with new balance
			# and return a tuple consisting of the author, and their balance

	@commands.command(pass_context=True)
	async def withdraw(self, ctx, address:str , amount:float):
		"""withdraws coins from wallet"""
		port =  "11311"

		author_name = str(ctx.message.author)
		
		self.check_for_user(author_name)

		#user_addy = rpcdat('getaddressesbyaccount',[author_name],port)
		#deposite_addr = user_addy[0]

		to_exec = " SELECT balance,lastblockhash FROM db WHERE user LIKE %s "
		user_bal = 0.0

		self.cursor.execute(to_exec,(author_name))
		result_set = self.cursor.fetchone()
		
		if result_set["lastblockhash"] == "0":
			user_bal = await self.parse_whole_bal(result_set,author_name)
		else:
			user_bal = await self.parse_part_bal(result_set,author_name)
		
		self.cursor.execute(to_exec,(author_name))
		result_set = self.cursor.fetchone()
		
		if float(result_set["balance"]) < amount:
                    await self.bot.say("**:warning:You cannot withdraw more money than you have!:warning:**")
		    return
		else:
			conf = self.rpc.validateaddress(address)     
			if not conf["isvalid"]:
				await self.bot.say("**:warning:Invalid address!:warning:**")
				return
			
	        self.rpc.withdraw(author_name,address, str(amount))
                await self.parse_part_bal(result_set, author_name)
		await self.bot.say("**Withdrew {} NET! :money_with_wings:**".format(str(amount)))
		

			
		# removes `message` amount from `wallet` and adds `message` amount to `address` provided
                    
                    
"""		
		try:
			if user_addy[0] == "":
				new_user_addy = rpcdat('',)
			else:
						
		except IndexError:
			await self.bot.say("You don't have an account.")
"""
def setup(bot):
	bot.add_cog(withdraw(bot))
