import logging
from googlesearch import search
from discord.ext import commands
import cogs

class WikiSearch(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.logger = logging.getLogger(__name__)

    @commands.Cog.listener()
    async def on_ready(self):
        self.logger.info('%s cog has been loaded.', self.__class__.__name__.title())

    @commands.command(name='search')
    async def lotr_search(self, ctx, *, query):
        '''
        searches on tolkiengateway.net for a given entry
        '''
        site = self.bot.config['google']['site']
        content = list(search(f'{query} site:{site}', lang='en', num_results=1))

        if not content:
            await ctx.send(':x: No results for `{}` on  *{}*.'.format(query, site))
            return
        content = content[0]
        title = f':mag: 1st result for `{query}` on  *{site}* :'
        await ctx.send(embed=cogs._dcutils.create_embed(title=title, content=content))

def setup(bot):
    bot.add_cog(WikiSearch(bot))