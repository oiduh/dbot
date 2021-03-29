from discord.ext import commands
from discord import Embed


def mod(ctx):
    author_roles = [role.id for role in ctx.author.roles]
    return bool(set(author_roles) & set(ModStuff.mod_ids).union({ModStuff.owner_id}))


def owner(ctx):
    author_roles = [role.id for role in ctx.author.roles]
    return ModStuff.owner_id in author_roles


is_mod = commands.check(mod)
is_owner = commands.check(owner)


class ModStuff(commands.Cog):

    mod_ids = []
    owner_id = -1

    def __init__(self, bot):
        self.bot = bot
        ModStuff.mod_ids = self.bot.mod_ids
        ModStuff.owner_id = self.bot.owner_id
        print(f'mod ids: {ModStuff.mod_ids}')
        self.commands = [cmd.name for cmd in self.get_commands()]
        print('ModStuff initialized')
        print(f'    Cog commands: {self.commands}')
        print(f'    owner role id:{self.bot.owner_id}')

    def get_server_roles(self, server):
        roles = [role.id for role in server.roles]
        return roles

    def check_valid_id(self, role_id, server):
        if not role_id.isdigit():
            return False
        role_id = int(role_id)
        server_roles = self.get_server_roles(server)
        if role_id not in server_roles:
            return False
        else:
            return True

    @is_mod
    @commands.command(name='getMods',
                      help="""
                           Get all members of the server who are authorized to control the bot
                           """)
    async def get_mods(self, ctx):
        member_list = []
        owner_id = set([self.bot.owner_id] + self.bot.mod_ids)
        for member in ctx.guild.members:
            member_roles = set([role.id for role in member.roles])
            if owner_id.intersection(member_roles):
                member_list.append(member.name)
        await ctx.send(member_list)

    @is_owner
    @commands.command(name='enableControl',
                      help="""
                           Enable control for bot commands for given role ID
                           """)
    async def enable_control(self, ctx, *args):
        if len(args) == 0:
            await ctx.send('ID missing')
            return
        role_id = args[0]
        if not self.check_valid_id(role_id, ctx.guild):
            await ctx.send('Invalid ID')
            return

        role_id = int(role_id)
        role_name = ctx.guild.get_role(role_id).name
        if role_id in self.bot.mod_ids:
            await ctx.send('This role "{role_name}" has already control over the bot.')
        else:
            self.bot.mod_ids.append(role_id)
            ModStuff.mod_ids.append(role_id)
            await ctx.send(f'The role "{role_name}" has now control over bot commands.')

    @is_owner
    @commands.command(name='removeControl',
                      help="""
                           Remove control for bot commands for given role ID
                           """)
    async def remove_control(self, ctx, *args):
        if len(args) == 0:
            await ctx.send('ID missing')
            return

        role_id = args[0]
        if not self.check_valid_id(role_id, ctx.guild):
            await ctx.send('Invalid ID')
            return

        role_id = int(role_id)
        if role_id == self.bot.owner_id:
            await ctx.send('Can\'t remove bot control for owner.')
            return
        elif role_id not in self.bot.mod_ids:
            await ctx.send('The role had not control to begin with.')
        else:
            self.bot.mod_ids.remove(role_id)
            ModStuff.mod_ids.remove(role_id)
            role_name = ctx.guild.get_role(role_id).name
            await ctx.send(f'The role "{role_name}" has no control over bot commands anymore.')

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        bot_channel = self.bot.get_channel(self.bot.channel)
        await bot_channel.send(f'The role "{role.name}" was deleted!')

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        bot_channel = self.bot.get_channel(self.bot.channel)
        await bot_channel.send(f'The role "{role.name}" was created!')

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        bot_channel = self.bot.get_channel(self.bot.channel)

        embed_msg = Embed(title='Role Changes', color=0xff0000)
        permissions_before = "\n> * ".join([permission[0] for permission in before.permissions if permission[1]])
        permissions_after = "\n> * ".join([permission[0] for permission in after.permissions if permission[1]])
        embed_msg.add_field(name='Old', value=
                            f'> name: {before.name}\n'
                            f'> id: {before.id}\n'
                            f'> color: {before.color}\n'
                            f'> position: {before.position}\n'
                            f'> mentionable: {before.mentionable}\n'
                            f'> permissions:\n> * {permissions_before}', inline=True)
        embed_msg.add_field(name='New', value=
                            f'> name: {after.name}\n'
                            f'> id: {after.id}\n'
                            f'> color: {after.color}\n' 
                            f'> position: {after.position}\n'
                            f'> mentionable: {after.mentionable}\n'
                            f'> permissions:\n> * {permissions_after}', inline=True)
        await bot_channel.send(embed=embed_msg)

# TODO: add whole role info description -> similar to on_role_update message -> e.g.: !getRoleInfo
