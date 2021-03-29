from discord.ext import commands
import json
import os
from datetime import datetime
from ModStuff import is_mod


class Responses(commands.Cog):

    responses_dict = {}
    response_cooldown = 5 * 60 # 5 minutes cooldown

    def __init__(self, bot):
        self.bot = bot
        self.commands = [cmd.name for cmd in self.get_commands()]
        self.prefix_length = len(self.bot.command_prefix)
        self.get_response_dict()
        print('Responses initialized')
        print(f'    Cog commands: {self.commands}')

    def get_response_dict(self):
        if os.path.exists('responses.json'):
            with open('responses.json', 'r') as read_file:
                Responses.responses_dict = json.load(read_file)
                read_file.close()
        else:
            Responses.responses_dict = {}

    @is_mod
    @commands.command(name='addResponse',
                      help="Add a response to a keyword, needs 2 arguments (keyword and response).")
    async def add_response(self, ctx, *args):
        words = [x for x in args]
        if len(words) < 2:
            await ctx.send(f'Hey {ctx.author.mention}, you need a keyword and a response for this command.')
        else:
            key_word = words[0]
            response = words[1]
            Responses.responses_dict[key_word] = {
                'response': response,
                'last_called': -1
                }
            with open('responses.json', 'w') as output_file:
                json.dump(Responses.responses_dict, output_file)
                output_file.close()
            await ctx.send(f'Response for keyword "{key_word}" added/changed.')

    @is_mod
    @commands.command(name='getResponses',
                      help="Display all keywords that have a response.")
    async def get_responses(self, ctx, *args):
        response_key_words = Responses.responses_dict.keys()
        if len(response_key_words) == 0:
            await ctx.send('There are no keywords yet.')
        else:
            response_string = ", ".join(response_key_words)
            await ctx.send(f'Responses available for: {response_string}.')

    @is_mod
    @commands.command(name='removeResponse',
                      help="Remove a response for a given keyword.")
    async def delete_response(self, ctx, *args):
        words = [x for x in args]
        if len(words) == 0:
            await ctx.send(f'You didn\'t write a keyword')
        else:
            key_word = words[0].lower()
            if key_word not in Responses.responses_dict:
                await ctx.send(f'There is no response for the keyword "{key_word}".')
            else:
                del Responses.responses_dict[key_word]
                with open('responses.json', 'w') as output_file:
                    json.dump(Responses.responses_dict, output_file)
                    output_file.close()
                await ctx.send(f'Response for keyword "{key_word}" was removed.')

    @is_mod
    @commands.command(name='changeCooldown',
                      help="Change the global cooldown for a response (given in seconds)")
    async def change_cooldown(self, ctx, *args):
        msg_content = [arg for arg in args]
        if msg_content[0].isdigit():
            new_cd = int(msg_content[0])
            if new_cd < 1:
                await ctx.send('Cooldown needs to be >0 seconds')
            else:
                Responses.response_cooldown = new_cd
                await ctx.send(f'Response cooldown set to {new_cd} seconds')
        else:
            await ctx.send('Cooldown must be a number.')

    @commands.Cog.listener()
    async def on_message(self, message):
        key_word = message.content.lower()
        if message.author == self.bot.user or key_word[self.prefix_length:] in self.commands:
            return
        if key_word in Responses.responses_dict:
            last_timestamp = Responses.responses_dict[key_word]['last_called']
            msg_timestamp = message.created_at.timestamp()
            if last_timestamp == -1 or msg_timestamp - last_timestamp > Responses.response_cooldown:
                Responses.responses_dict[key_word]['last_called'] = msg_timestamp
                await message.channel.send(Responses.responses_dict[key_word]['response'])
            else:
                cooldown = (Responses.response_cooldown - (msg_timestamp - last_timestamp))
                cooldown = datetime.fromtimestamp(cooldown).strftime('%M min %S sec')
                await message.delete()
                await message.channel.send(f'"{key_word}" on cooldown. Available in {cooldown} again', delete_after=5)
