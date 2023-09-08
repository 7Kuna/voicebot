import json
import discord
from discord.ext import commands
from OwnerCog import OwnerCog
from SetupCog import SetupCog
from PrivateCog import PrivateCog
from MiscCog import MiscCog

with open('config.json', 'r') as f:
    config = json.load(f)

intents = discord.Intents.all()
bot = commands.Bot(command_prefix=config['prefix'], description="Un bot de gestion de vocales", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.add_cog(OwnerCog(bot))
    await bot.add_cog(SetupCog(bot))
    await bot.add_cog(PrivateCog(bot))
    await bot.add_cog(MiscCog(bot))
    print('Cogs added')


bot.run(config['token'])
