from core.bot import bot

@bot.event
async def on_message(message):
    if message.content.startswith('!test'):
        await bot.send_message(message.channel,'Test!')