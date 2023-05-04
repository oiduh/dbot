import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from Responses import Responses
from ModStuff import ModStuff
from MusicPlayer import MusicPlayer


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
OWNER = os.getenv('DISCORD_OWNER')
SERVER = os.getenv('DISCORD_SERVER')
CHANNEL = os.getenv('DISCORD_BOT_CHANNEL')


class dbot(commands.Bot):

    def __init__(self, command_prefix, case_insensitive, self_bot, owner_id, server, channel, intents):
        commands.Bot.__init__(self, command_prefix=command_prefix,
                              case_insensitive=case_insensitive, self_bot=self_bot,
                              intents=intents)
        if not owner_id.isdigit() or not server.isdigit() or not channel.isdigit():
            raise Exception
        self.owner_id = int(owner_id)
        self.mod_ids = []
        self.server = int(server)
        self.channel = int(channel)
        print('dbot initialized')
        print(f'    owner role id: {self.owner_id}')


# needed to have access to all server members
intents = discord.Intents.default()
intents.members = True

bot = dbot(command_prefix='!', case_insensitive=True, self_bot=False,
                 owner_id=OWNER, server=SERVER, channel=CHANNEL, intents=intents)

@bot.event
async def on_ready():
    for guild in bot.guilds:
        if guild.id == bot.server:
            await guild.owner.send('bot added to your server')
        else:
            await bot.leave_guild(guild)

@bot.event
async def on_guild_join(guild):
    if guild.id != bot.server:
        await guild.owner.send('you cant add this bot, it\'s private')
        await bot.leave_guild(guild)


bot.add_cog(ModStuff(bot))
bot.add_cog(Responses(bot))
bot.add_cog(MusicPlayer(bot))
bot.run(TOKEN)

# TODO:
#   ModStuff: more commands to manage server (ban, kick etc.)
#   MusicPlayer: queue system, keyword search (currently only links), spotify integration (meta data), role dependency
#   Responses: limit amount, cooldown reset etc.
