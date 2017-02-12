import imp
import os, sys, time, json
from utils.parsing import parse_json
from utils import output
from lib import discord

sys.path += ['lib']

home = os.getcwd()

output = output.PrOut()

bot = discord.Client()

class J():
	def __init__(self, raw_config):
		self.load = []
		self.unload = []
		self.raw_config = raw_config
		self.doc = {}
		self.times = {}
		self.modules = []
		self.cmds = {}
		self.data = {}
		self.webserver_data = {}
		self.bot_startup = int(time.time())
		# Setup modules
		self.setup()

	def config(self, key=None, default=None):
		if not key:
			return self.raw_config
		if key in self.raw_config:
			return self.raw_config[key]
		else:
			if default:
				return default
				return False

	def setup(self):
		self.variables = {}

		filenames, core_filenames = [], []
		for fn in os.listdir(os.path.join(home, 'modules')):
			if fn.endswith('.py') and not fn.startswith('_'):
				if self.config('whitelisted_modules', False):
					if fn.split('.', 1)[0] not in self.config('whitelisted_modules', []):
						continue
				filenames.append(os.path.join(home, 'modules', fn))

		# Add system modules that the user should always require. Still can
		#  be removed by deleting them or moving them out of the system
		#  modules directory
		for fn in os.listdir(os.path.join(home, 'core/modules')):
			if fn.endswith('.py') and not fn.startswith('_'):
				filenames.append(os.path.join(home, 'core/modules', fn))
				core_filenames.append(fn.split('.', 1)[0])

		excluded_modules = self.raw_config["data"]
		if self.load:
			for filename in self.load:
			# Add user specified modules on reload
				if filename in filenames:
					continue
				try:
					fn = os.path.join(home, 'modules', filename + '.py')
					filenames.append(fn)
				except:
					continue
		filenames = sorted(list(set(filenames)))
		# Reset some variables that way we don't get dups
		self.modules = []
		self.cmds = {}

		# Load modules
		for filename in filenames:
			name = os.path.basename(filename)
			if name in excluded_modules:
			# If the file was excluded via the config file
			# Don't exclude if purposely loaded
				continue
			if name in self.unload:
			# If the module was excluded via the reload module
				continue
			# if name in sys.modules:
			#     del sys.modules[name]
			self.setup_module(name, filename)

		tmp_modules = []
		for module in self.modules:
			if module not in core_filenames:
				tmp_modules.append(module)
		if core_filenames:
			#output.info('Loaded {} core modules: {}'.format(
			#	len(core_filenames), ', '.join(core_filenames)))
			output.info('Loaded '+str(len(core_filenames))+' core modules: '+str(core_filenames))
		if self.modules:
			#output.info('Loaded {} modules: {}'.format(
			#	len(tmp_modules), ', '.join(tmp_modules)))
			output.info('Loaded {} modules: {}'+
				str(len(tmp_modules)), ', '.join(core_modules))
		else:
			output.warning('Couldn\'t find any modules')
		self.connect()

	def setup_module(self, name, filename, is_startup=True):
		try:
			module = imp.load_source(name, filename)
			if hasattr(module, 'setup'):
				module.setup(self)
			self.register(vars(module))
			self.modules.append(name)
			self.modules = sorted(list(set(self.modules)))
		except Exception as e:
			output.error("Failed to load %s: %s" % (name, e))
			if not is_startup:
				# Only raise exception again if it's user-triggered
				raise Exception("Failed to load %s: %s" % (name, e))

	def get(self, key):
		if key in self.data:
			return self.data[key]
		else:
			return False

	def set(self, key, data):
		try:
			self.data[key] = data
			return True
		except:
			return False

	def connect(self):
		description = """Core module/initial Discord connection
Connecting using the token found in config.json"""

		@bot.event
		async def on_ready():
			output.info('Logged in as '+bot.user.name)
		try:
			bot.run(self.raw_config["data"][0]["token"])
		except KeyboardInterrupt:
			output.success('KeyboardInterrupt: Shutting down bot...')