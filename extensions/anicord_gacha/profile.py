from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from utilities.bases.cog import AGBCog
from utilities.embed import Embed

if TYPE_CHECKING:
    from utilities.bases.context import AGBContext


class Player:
    def __init__(self, user: discord.Member | discord.User, blombos: int) -> None:
        super().__init__()
        self.user = user
        self.blombos = blombos


class Profile(AGBCog):
    @commands.hybrid_command()
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def balance(self, ctx: AGBContext, user: discord.Member = commands.Author) -> None:
        data = await self.bot.pool.fetchrow(
            """
            SELECT
                blombos
            FROM
                PLayerData
            WHERE
                user_id = $1
            """,
            user.id,
        )

        if not data:
            return  # This should usually never run

        player = Player(user, data['blombos'])

        await ctx.reply(embed=Embed(title=f"{user}'s balance", description=f'`{player.blombos}` blombos.'))
