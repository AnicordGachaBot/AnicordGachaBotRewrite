from __future__ import annotations

import operator
from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext import commands, menus

from utilities.bases.cog import AGBCog
from utilities.embed import Embed
from utilities.pagination import Paginator

if TYPE_CHECKING:
    import asyncpg

    from utilities.bases.context import AGBContext


class BlombosLBPageSource(menus.ListPageSource):
    def __init__(self, entries: list[tuple[int, asyncpg.Record]]) -> None:
        super().__init__(entries, per_page=10)

    async def format_page(self, _: Paginator, page: list[tuple[int, asyncpg.Record]]) -> Embed:
        embed = Embed(
            title='Blombos leaderboard',
            description='\n'.join(f'{p[0]}. <@{p[1]["user_id"]}> - **`{p[1]["blombos"]}`**' for p in page),
        )
        embed.set_footer(text=f'You are #{int([a for a in self.entries if a[1]["user_id"] == _.ctx.author.id][0][0]) + 1}')  # noqa: RUF015

        return embed


class Leaderboard(AGBCog):
    @commands.hybrid_command(aliases=['blombolb'])
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def blombos_leaderboard(self, ctx: AGBContext) -> None:
        data = await self.bot.pool.fetch("""SELECT * FROM PlayerData""")

        enumerated_data = list(
            enumerate(
                sorted(
                    data,
                    key=operator.itemgetter('blombos'),
                    reverse=True,
                ),
            )
        )

        paginate = Paginator(BlombosLBPageSource(enumerated_data), ctx=ctx)

        await paginate.start()
