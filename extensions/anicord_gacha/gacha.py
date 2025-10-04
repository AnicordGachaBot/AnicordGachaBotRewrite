from __future__ import annotations

import datetime
import secrets
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from extensions.anicord_gacha.bases import (
    BURN_WORTH,
    PULL_INTERVAL,
    RARITY_COLOURS,
    RARITY_PULL_MESSAGES,
    RARITY_WEIGHTS,
    Card,
    ThemeConverter,
    rarity_emoji_gen,
)
from utilities.bases.cog import AGBCog
from utilities.embed import Embed
from utilities.functions import fmt_str

if TYPE_CHECKING:
    from discord import Message

    from utilities.bases.context import AGBContext

theme_param = commands.parameter(converter=ThemeConverter)


class Gacha(AGBCog):
    async def get_random_rarity(self, theme: str) -> int | None:
        rarities_data = await self.bot.pool.fetch(
            """
            SELECT DISTINCT
                rarity
            FROM
                Cards
            WHERE
                LOWER(theme) = $1
            """,
            theme.lower(),
        )

        if not rarities_data:
            return None

        rarities = [r['rarity'] for r in rarities_data]
        weights = [RARITY_WEIGHTS[w] for w in rarities]

        cumulative_distribution = {}

        cumulative_distribution[0] = weights[0]

        for i in range(1, len(weights)):
            cumulative_distribution[i] = cumulative_distribution[i - 1] + weights[i]

        # TODO: The above logic is supposed to be improved.

        dice = secrets.SystemRandom().random()

        for i in range(len(cumulative_distribution)):
            if dice < cumulative_distribution[i]:
                return rarities[i]

        return rarities[-1]

    async def get_random_card(self, theme: str) -> Card | None:
        rarity = await self.get_random_rarity(theme)

        if not rarity:
            return None

        card = await self.bot.pool.fetchrow(
            """
            SELECT
                *
            FROM
                Cards
            WHERE
                LOWER(theme) = $1
                AND rarity = $2
            ORDER BY
                RANDOM()
            LIMIT
                1
            """,
            theme.lower(),
            rarity,
        )

        if not card:
            return None

        return Card(
            card['id'],
            name=card['name'],
            rarity=card['rarity'],
            theme=card['theme'],
            image=card['image_path'],
            is_obtainable=card['is_obtainable'],
        )

        # NOTE: We dont fetch themselves because we dont need the data
        # Instead we random integer with the count

    @commands.hybrid_command()
    async def pull(self, ctx: AGBContext, theme: str = theme_param) -> Message:
        pull_interval = await self.bot.pool.fetchrow(
            """
            SELECT
                *
            FROM
                PullIntervals
            WHERE
                user_id = $1
                AND LOWER(theme) = $2
            """,
            ctx.author.id,
            theme.lower(),
        )

        if pull_interval:
            last_pulled: datetime.datetime = pull_interval['last_pull']
            if datetime.datetime.now(datetime.UTC) < last_pulled + PULL_INTERVAL:
                return await ctx.reply('You cannot pull now!')

        card = await self.get_random_card(theme)

        if not card:
            return await ctx.reply('Sorry, this theme has no card.')

        new_inventory_entry = await card.give(self.bot.pool, user=ctx.author)

        if new_inventory_entry is None:
            raise commands.CommandError('Inventory Entry was found to be None')

        is_new = not int(new_inventory_entry['quantity']) > 1

        await self.bot.pool.execute(
            """
            INSERT INTO
                PullIntervals (user_id, theme, last_pull)
            VALUES
                (
                    $2,
                    (
                        SELECT
                            name
                        FROM
                            Themes
                        WHERE
                            LOWER(name) = LOWER($3)
                    ),
                    $1
                )
            ON CONFLICT (user_id, theme) DO UPDATE
            SET
                last_pull = $1
            """,
            datetime.datetime.now(datetime.UTC),
            ctx.author.id,
            theme,
        )

        embed = Embed(
            title=card.name,
            description=fmt_str(
                [
                    f'Rarity: {"".join(rarity_emoji_gen(card.rarity))}',
                    f'Burn Worth: {BURN_WORTH[card.rarity]}',
                    f'ID: {card.id}',
                ],
                seperator='\n',
            ),
            colour=discord.Colour.from_str(RARITY_COLOURS[card.rarity]),
        )
        embed.set_image(url=card.image)
        if is_new:
            embed.set_footer(text='NEW!')

        return await ctx.reply(
            content=f'{ctx.author.mention} {RARITY_PULL_MESSAGES[card.rarity]}',
            embed=embed,
        )
