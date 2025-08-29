from __future__ import annotations

import secrets
from typing import TYPE_CHECKING

from discord import Message
from discord.ext import commands

from extensions.anicord_gacha.bases import Card
from utilities.bases.cog import AGBCog
from utilities.embed import Embed
from utilities.functions import fmt_str

if TYPE_CHECKING:
    from utilities.bases.context import AGBContext

RARITY_WEIGHTS = {
    1: 0.4395,
    2: 0.4,
    3: 0.1,
    4: 0.05,
    5: 0.01,
    6: 0.0005,
}


class Gacha(AGBCog):
    async def get_random_rarity(self, theme: str) -> int | None:
        rarities_data = await self.bot.pool.fetch(
            """SELECT DISTINCT rarity FROM Cards WHERE theme = $1""",
            theme,
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
            """SELECT * FROM Cards WHERE theme = $1 AND rarity = $2 ORDER BY RANDOM() LIMIT 1""",
            theme,
            rarity,
        )

        if not card:
            return None

        return Card(
            card['id'],
            name=card['name'],
            rarity=card['rarity'],
            theme=card['theme'],
            image=card['image_url'],
            is_obtainable=card['is_obtainable'],
        )

        # NOTE: We dont fetch themselves because we dont need the data
        # Instead we random integer with the count

    @commands.command()
    async def pull(self, ctx: AGBContext, theme: str) -> Message:
        card = await self.get_random_card(theme)

        if not card:
            return await ctx.reply('Sorry, this theme has no card.')

        embed = Embed(
            title='Ayy lmao',
            description=fmt_str(
                [
                    f'ID: {card.id}',
                    f'Name: {card.name}',
                ],
                seperator='\n',
            ),
        )
        embed.set_image(url=card.image)

        return await ctx.reply(embed=embed)
