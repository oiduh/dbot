from discord.ext import commands
from discord import Embed
from ModStuff import is_owner, is_mod
import discord
from YouTubeDownloader import DownloadStatus, YoutubeDownloader


class MusicPlayer(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.vc_id = -1
        self.vc_client = None
        self.downloader = YoutubeDownloader('music')
        print('MusicPlayer initialized')

    @commands.command(name='assignVC',
                      help="Use this command with 1 additional argument, which represents the Voice Channel with "
                           "either the name or id\n"
                           "Usage examples:\n"
                           "    '!assignVC General' or\n"
                           "    '!assignVC 684870763014389817'")
    async def assign_vc(self, ctx, name_or_id=None):
        if not name_or_id:
            await ctx.send('you didn\'t specify a VC name/id')
        else:
            if name_or_id.isdigit():
                trgt_vc_id = int(name_or_id)
                vc_lambda = lambda vc: vc.id == trgt_vc_id
            else:
                trgt_vc_name = name_or_id
                vc_lambda = lambda vc: vc.name == trgt_vc_name
            trgt_vc = next(filter(vc_lambda, ctx.guild.voice_channels), None)
            if not trgt_vc:
                await ctx.send('There is no voice channel with your name/id specification')
            else:
                self.vc_id = trgt_vc.id
                await ctx.send(f'Bot assigned to: {trgt_vc.name}({trgt_vc.id})')

    @commands.command(name='unassignVC',
                      help="This command removes its assigned Voice Channel, if it existed.\n"
                           "Notice, that the bot cannot join a Voice Channel, "
                           "if there's no Voice Channel assigned to it!")
    async def unassign_vc(self, ctx):
        if self.vc_id == -1:
            await ctx.send('Bot wasn\'t even assigned to a vc, WTFF')
        else:
            self.vc_id = -1
            await ctx.send('Bot is not assigned to a VC anymore')

    @commands.command(name='joinVC',
                      help="This command makes the bot join its dedicated Voice Channel, "
                           "specified with the command '!assignVC [name_or_id]'")
    async def join_vc(self, ctx):
        if self.vc_client:
            await ctx.send(f'Bot is already connected to: {self.vc_client.channel.name}')
        elif self.vc_id == -1:
            await ctx.send('you need to specify a channel for the bot')
        else:
            vc = next(filter(lambda x: x.id == self.vc_id, ctx.guild.voice_channels), None)
            if not vc:
                await ctx.send('couldn\'t find the channel, WTFF')
            else:
                await ctx.send(f'joining vc: {vc.name}')
                await vc.connect()
                self.vc_client = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

    @commands.command(name='leaveVC',
                      help="Use this command to make the bot leave the Voice Channel its currently connected to")
    async def leave_vc(self, ctx):
        # TODO: this might be a little ugly now -> rework later
        if self.vc_client:
            await ctx.send(f'leaving: {self.vc_client.channel.name}')
            self.vc_client = None
            await ctx.voice_client.disconnect()
        else:
            await ctx.send('Bot is currently not connected to a VC')

    @commands.command(name='getVC',
                      help="Use this command to find out which Voice Channel is currently assigned to the bot.")
    async def get_vc(self, ctx):
        if self.vc_id == -1:
            await ctx.send('There is currently no VC assigned to the bot')
        else:
            vc = next(filter(lambda x: x.id == self.vc_id, ctx.guild.voice_channels), None)
            if not vc:
                await ctx.send('Can\'t find a channel, WTFF !')
            else:
                await ctx.send(f'Bot is currently assigned to: {vc.name}({vc.id})')

    # temporary solution -> only plays one song at the moment
    @commands.command(name='play',
                      help="TODO")
    async def play(self, ctx, *args):
        if self.vc_client.is_connected():
            '''download_status, filename = download_video_as_mp3(yt_link)
            if download_status == DownloadStatus.SUCCESS:
                song_path = 'music/' + filename
                if self.vc_client.is_playing():
                    self.vc_client.stop()
                await ctx.send(f'playing song: {filename}')
                self.vc_client.play(
                    discord.FFmpegPCMAudio(executable='C:\\Program Files (x86)\\ffmpeg\\bin\\ffmpeg.exe',
                                           source=song_path)
                )
            else:
                await ctx.send('Invalid YouTube link!')'''
            search_results = self.downloader.search(" ".join(args))
            if len(search_results) > 0:
                embed_msg = Embed(title='Search Results', color=0xff0000)
                for index, (title, yt_url) in enumerate(search_results):
                    embed_msg.add_field(name=f'#{index}', value=
                    f'title: {title}\n'
                    f'url: {yt_url}\n', inline=False)
                message = await ctx.send(embed=embed_msg)
                for emoji in ['\u0031\u20e3', '\u0032\u20e3', '\u0033\u20e3', '\u0034\u20e3', '\u0035\u20e3']:
                    await message.add_reaction(emoji)
                await ctx.send(f'{ctx.author.mention} react with one of the numbers to play your song.')
            else:
                await ctx.send('no results found for your query')

        else:
            await ctx.send('bot is not connected to a voice channel')

    @commands.command(name='pause',
                      help="TODO")
    async def pause(self, ctx):
        if self.vc_client.is_connected() and self.vc_client.is_playing():
            self.vc_client.pause()
            await ctx.send('song paused')
        else:
            await ctx.send('the bot is either not connected or not playing any music')

    @commands.command(name='resume',
                      help="TODO")
    async def resume(self, ctx):
        if self.vc_client.is_connected() and self.vc_client.is_paused():
            self.vc_client.resume()
            await ctx.send('song resumed')
        else:
            await ctx.send('the bot is either not connected or playing music')

    @commands.command(name='stop',
                      help="TODO")
    async def stop(self, ctx):
        if self.vc_client.is_connected() and \
                self.vc_client.is_playing() or self.vc_client.is_paused():
            self.vc_client.stop()
            await ctx.send('song stopped')
        else:
            await ctx.send('the bot is either not connected or not playing any music')

    # TODO:
    #   implement tracking of guild channel updates
    #   discord.on_guild_channel_update(before, after)
    #   discord.on_guild_channel_delete(channel)
    #   discord.on_guild_channel_create(channel)
    #   implement queue system:
    #     example commands: add, remove, clear, skip, jump-to,

    # TEST COMMAND
    @commands.command(name='joined',
                      help="TODO")
    async def joined(self, ctx):
        print(help(self.assign_vc))
        await ctx.send(self.bot.voice_clients)
