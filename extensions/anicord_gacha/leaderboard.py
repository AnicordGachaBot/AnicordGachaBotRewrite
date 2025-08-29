from __future__ import annotations

from typing import TYPE_CHECKING

from discord import app_commands
from discord.ext import commands, menus

from extensions.anicord_gacha.blombos import Player
from utilities.bases.cog import AGBCog
from utilities.embed import Embed
from utilities.pagination import Paginator

if TYPE_CHECKING:
    from utilities.bases.context import AGBContext


class BlombosLBPageSource(menus.ListPageSource):
    def __init__(self, entries: list[Player]) -> None:
        sorted_entries = list(enumerate(sorted(entries, reverse=True, key=lambda p: p.blombos)))
        super().__init__(sorted_entries, per_page=10)

    async def format_page(self, _: Paginator, page: list[tuple[int, Player]]) -> Embed:
        return Embed(
            title='Blombos leaderboard',
            description='\n'.join(f'{p[0]}. {p[1].user.mention} - **`{p[1].blombos}`**' for p in page),
        )


class Leaderboard(AGBCog):
    @commands.hybrid_command(aliases=['blombolb'])
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def blombos_leaderboard(self, ctx: AGBContext) -> None:
        data = await self.bot.pool.fetch("""SELECT * FROM PlayerData""")

        players = [
            Player(
                p,
                d['blombos'],
            )
            for d in data
            if (p := self.bot.get_user(d['user_id'])) and p
        ]

        paginate = Paginator(BlombosLBPageSource(players), ctx=ctx)

        await paginate.start()
