from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from extensions.anicord_gacha.bases import RARITY_COLOURS, Card
from utilities.bases.cog import AGBCog
from utilities.embed import Embed

if TYPE_CHECKING:
    from utilities.bases.context import AGBContext


class Player:
    def __init__(
        self,
        user: discord.Member | discord.User,
        blombos: int,
        bio: str | None = None,
        wallpaper: Card | None = None,
    ) -> None:
        super().__init__()
        self.user = user
        self.blombos = blombos
        self.bio = bio
        self.wallpaper = wallpaper


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

    @commands.hybrid_group(name='profile', fallback='view')
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.allowed_installs(guilds=True, users=True)
    async def profile_view(self, ctx: AGBContext, user: discord.Member = commands.Author) -> discord.Message:
        data = await self.bot.pool.fetchrow(
            """
            SELECT
                d.*,
                c as card_data,
                EXISTS (
                    SELECT
                        1
                    FROM
                        CardInventory
                    WHERE
                        user_id = $1
                        AND id = d.wallpaper
                ) as is_in_inventory
            FROM
                PLayerData d
                JOIN Cards c ON d.wallpaper = c.id
            WHERE
                d.user_id = $1
            """,
            user.id,
        )

        if not data:
            return await ctx.reply(f'{user} does not have a profile.')

        profile_data = Player(
            user,
            data['blombos'],
            data['bio'],
            Card(
                data['card_data']['id'],
                name=data['card_data']['name'],
                rarity=data['card_data']['rarity'],
                theme=data['card_data']['theme'],
                image=data['card_data']['image_url'],
            )
            if data['is_in_inventory'] is True
            else None,
        )

        embed = Embed(
            title=f"{user}'s profile",
            description=profile_data.bio,
            colour=discord.Colour.from_str(
                RARITY_COLOURS[profile_data.wallpaper.rarity],
            )
            if profile_data.wallpaper
            else None,
        )

        embed.set_image(url=profile_data.wallpaper.image if profile_data.wallpaper else None)

        return await ctx.reply(embed=embed)
