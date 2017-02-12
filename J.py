#!/usr/bin/env python3.5
"""
J-Discord Copyright (C) 2017 Aareon Sullivan
Source/docs: https://github.com/Aareon/J-Discord
"""

import sys, os, time, re, json, asyncio
from core import bot
from utils import output, parsing

output = output.PrOut()

async def main():
    # Require python 3 or later
    if sys.version_info < (3, 5):
        output.error('Requires Python 3.5.X, from www.python.org')
        sys.exit(1)
    output.success('Initializing the bot, this could take a minute')

    # Load The Configuration
    bot_config = 'config.json'

    # and check if it exists
    if not os.path.isfile(bot_config):
        output.error(
            'Configuration file "%s" does not exist. Please copy '
            'the example.json to config.json then run J again' % bot_config)
        sys.exit(1)

    try:
        config = parsing.parse_json(bot_config)
    except Exception as e:
        output.error('The config file has syntax errors. Please fix them and run J again!\n' + str(e))
        sys.exit(1)
    await connect(config)

    try:
        # set some temporary variables that we will be using for config
        # file version checking
        conf_last_check = int(time.time())
        conf_last_mtime = int(os.path.getmtime(bot_config))
        while True:
            time.sleep(1)
            if (int(time.time()) - conf_last_check) > 10 and int(os.path.getmtime(bot_config)) > conf_last_mtime:
                conf_last_check = int(time.time())
                conf_last_mtime = int(os.path.getmtime(bot_config))
                try:
                    # If the new configuration file isn't the same as the last
                    # one that we saved, attempt to re-import it
                    config_new = parsing.parse_json(bot_config)
                    output.sucess('Configuration file %s has changed! Use the restart command to take affect!' % bot_config)
                    config = config_new
                except Exception as e:
                    # Only spit out errors once per file modification
                    output.error("Configuration file has been changed, however I can not read it! (%s)" % str(e))
    except KeyboardInterrupt:
        output.success('KeyboardInterrupt: Shutting down bot...')

def connect(config):
    bot.J(config)

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()  
        asyncio.ensure_future(main())
        loop.run_forever()  
    except SystemExit:
        sys.exit()
    except KeyboardInterrupt:
        sys.exit()