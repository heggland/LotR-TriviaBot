from datetime import datetime
import logging
import os
import platform
import random
import typing
from discord.ext import commands
import discord

import cogs._dcutils


class Utils(commands.Cog):
    '''
    Utilities commands for the Bot.
    '''

    def __init__(self, bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)


    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('%s cog has been loaded.',
                         self.__class__.__name__.title())


    @commands.is_owner()
    @commands.command()
    async def reload(self, ctx, cog: typing.Optional[str] = ''):
        '''
        reloads all or one specific cog
        '''
        if cog:
            if os.path.isfile(f'./cogs/{cog}.py'):
                dc_cogs = [f'{cog}.py']
                title = f':clock10: Reloading `{cog}`'
            else:
                await ctx.send(':x: There is no cog with that name!')
                return
        else:
            dc_cogs = os.listdir('./cogs/')
            title = ':clock10: Reloading all cogs...'

        embed = discord.Embed(title=title,
                              description='Please wait, this will take a moment...')
        embed_msg = await ctx.send(embed=embed)

        for ext in dc_cogs:
            try:
                if ext.endswith('.py') and not ext.startswith('_'):
                    self.bot.unload_extension(f'cogs.{ext[:-3]}')
                    self.bot.load_extension(f'cogs.{ext[:-3]}')
                    embed.add_field(name=':white_check_mark: Reloaded:',
                                    value=ext[:-3],
                                    inline=True)
            except commands.errors.ExtensionFailed as exc:
                embed.add_field(name=':x: Failed:',
                                value=ext[:-3],
                                inline=True)
                print(exc)
        await embed_msg.edit(embed=embed)


    @commands.cooldown(1, 60)
    @commands.command()
    async def stats(self, ctx):
        '''
        displays misc. statistics about the bot
        '''
        embed = discord.Embed(title=f'Stats for {self.bot.user.name}')
        embed.colour = random.choice(self.bot.color_list)

        dtime = datetime.now() - self.bot.start_time
        embed.add_field(name=':snake: Python Version:',
                        value=platform.python_version())
        embed.add_field(name=':robot: Discord API Version:',
                        value=discord.__version__)
        embed.add_field(name=':stopwatch: Latency:',
                        value=f'{round(self.bot.latency*1000)}ms')
        embed.add_field(name=':alarm_clock: Uptime:', value=(
            f'{dtime.days}d,{dtime.seconds//3600}h,{dtime.seconds%3600//60}m,{dtime.seconds % 60}s'))
        embed.add_field(name=':shield: Guild Count:',
                        value=len(self.bot.guilds))
        embed.add_field(name=':technologist: Member Count:',
                        value=len(set(self.bot.get_all_members())))
        # embed.add_field(name=':jigsaw: Shard count:'
        #                 value=self.bot.shard_count)
        embed.add_field(name=':gear: Active Cogs:',
                        value=len(set(self.bot.cogs)))
        embed.add_field(name=':card_box: Github:',
                        value=self.bot.config['general']['github_repo'])
        embed.add_field(name=':floppy_disk: Developer:',
                        value='<@{}>'.format(self.bot.config['general']['developer_id']))
        await ctx.send(embed=embed)


    @commands.has_permissions(manage_channels=True)
    @commands.group(name='settings', aliases=['setting', 'config'], invoke_without_command=True)
    async def settings(self, ctx):
        '''
        configures which categories are activated.
        '''
        # user wants to see the config embed:
        embed = discord.Embed(
            title=f'Config for #{ctx.channel} in {ctx.guild}')

        for category in self.bot.config['discord']['settings']['categories']:

            server_setting = ':grey_question:'
            if ctx.guild.id in self.bot.settings.keys():
                if category in self.bot.settings[ctx.guild.id]:
                    server_setting = self.bot.config['discord']['indicators'][self.bot.settings[ctx.guild.id][category]]

            channel_setting = ':grey_question:'
            if ctx.channel.id in self.bot.settings.keys():
                if category in self.bot.settings[ctx.channel.id]:
                    channel_setting = self.bot.config['discord']['indicators'][
                        self.bot.settings[ctx.channel.id][category]]

            effective = self.bot.config['discord']['indicators'][cogs._dcutils.is_category_allowed(
                ctx, category, self.bot.settings, self.bot.config['discord']['settings']['defaults'])]
            embed.add_field(name=f'**Category `{category}`:**',
                            value=f'Server: {server_setting} Channel: {channel_setting} Effective: {effective}',
                            inline=False)
        embed.set_footer(
            text='Tip: If you want to change the settings, you need to provide arguments. Type "{} settings help" for more info.')
        await ctx.send(embed=embed)


    @commands.has_permissions(manage_channels=True)
    @settings.command(name='channel', aliases=['c', 'ch', 'local'])
    async def channel_settings(self, ctx, *args):
        '''
        selects settings for the channel
        '''
        await self.edit_settings(ctx, args, True)


    @commands.has_permissions(manage_channels=True)
    @settings.command(name='server', aliases=['s', 'srv', 'global'])
    async def server_settings(self, ctx, *args):
        '''
        selects settings for the server
        '''
        await self.edit_settings(ctx, args, False)


    @commands.has_permissions(manage_channels=True)
    @settings.command(name='info', aliases=['?'], invoke_without_command=True)
    async def help_settings(self, ctx):
        '''
        displays info about the settings
        '''
        text = self.bot.config['discord']['settings']['help'].format(self.bot.config['general']['prefix'][0],
                                                                     '`' + '`, `'.join(self.bot.config['discord']['settings']['categories']) + '`')
        await ctx.send(text, file=discord.File('assets/infographic1.png'))


    async def edit_settings(self, ctx, args, channel_mode):
        '''
        edits the settings according to user input
        '''
        error_str = ''
        if len(args) != 2:
            error_str = f'{self.bot.config["discord"]["indicators"][0]} You have to provide __two__ arguments!'
        elif args[0].lower() not in self.bot.config['discord']['settings']['categories']:
            error_str = f'{self.bot.config["discord"]["indicators"][0]} Invalid category!'
        elif args[1].lower() not in ['on', 'off', 'reset']:
            error_str = f'{self.bot.config["discord"]["indicators"][0]} Invalid mode!'

        if error_str:
            error_str += 'You have to provide a category and a mode to edit. The categories are:\n'
            error_str += '`' + \
                '`, `'.join(self.bot.config['discord']
                            ['settings']['categories']) + '`\n'
            error_str += 'The modes are:\n `on`, `off`, `reset`'
            await ctx.send(error_str)
            return

        spec_id = ctx.channel.id if channel_mode else ctx.guild.id
        spec_word = 'channel' if channel_mode else 'server'
        category, mode = args

        if not spec_id in self.bot.settings.keys():
            self.bot.settings[spec_id] = {}

        if mode == 'on':
            self.bot.settings[spec_id][category] = 1
            await ctx.send(f'category `{category}` was turned **on** for this {spec_word}.')

        elif mode == 'off':
            self.bot.settings[spec_id][category] = 0
            await ctx.send(f'category `{category}` was turned **off** for this {spec_word}.')

        elif mode == 'reset':
            if category in self.bot.settings[spec_id].keys():
                del self.bot.settings[spec_id][category]
                await ctx.send(f'category `{category}` was **unset** for this {spec_word}.')
            else:
                await ctx.send(f'category `{category}`was not yet set for this {spec_word} .')


    @commands.Cog.listener('on_command_error')
    async def on_command_error(self, ctx, error):
        '''
        An error handler that is called when an error is raised inside a command either through user input error, check failure, or an error in the code.
        '''
        # Ignore these errors
        ignored = (commands.CommandNotFound, commands.UserInputError, commands.NoPrivateMessage)
        if isinstance(error, ignored):
            return

        if isinstance(error, commands.CommandOnCooldown):
            # If the command is currently on cooldown trip this
            minutes, secs = divmod(error.retry_after, 60)
            hours, minutes = divmod(minutes, 60)
            if not hours and not minutes:
                await ctx.send(f' You must wait {round(secs)} seconds to use this command!')
            elif not hours and minutes:
                await ctx.send(f' You must wait {round(minutes)} minutes and {round(secs)} seconds to use this command!')
            else:
                await ctx.send(f' You must wait {round(hours)} hours, {round(minutes)} minutes and {round(secs)} seconds to use this command!')

        elif isinstance(error, cogs._dcutils.CategoryNotAllowed):
            # if the category is not allowed in this context
            await ctx.send(f'{self.bot.config["discord"]["indicators"][0]} The category `{error.category}` is disabled in this context.', delete_after=15)

        elif isinstance(error, (commands.MissingPermissions, commands.NotOwner)):
            await ctx.send('*\'You cannot wield it. None of us can.\'* ~Aragorn\nYou lack permission to use this command!')

        elif isinstance(error, cogs._dcutils.ChannelBusy):
            if ctx.channel.permissions_for(ctx.guild.me).manage_messages:
                await error.orig_message.delete()
            await ctx.send(f'{self.bot.config["discord"]["indicators"][0]} This channel is currently busy. Try again when no event is currently taking place.', delete_after=10)

        elif isinstance(error, commands.CheckFailure):
            await ctx.send(f'{self.bot.config["discord"]["indicators"][0]} An internal error occured while parsing this command. Please contact the developer.')
            self.logger.warning('Unknown CheckFailure occured, type is: %s',type(error))

        else:
            raise error


def setup(bot):
    bot.add_cog(Utils(bot))
