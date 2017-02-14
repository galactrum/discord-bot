import parsing

config = parsing.parse_json('config.json')

def is_owner(ctx):
    return ctx.message.author.id in config["owners"]