from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands, menus

from extensions.anicord_gacha.bases import (
    BURN_WORTH,
    RARITY_COLOURS,
    Card,
    GachaMemberConverter,
    InventoryCard,
    rarity_emoji_gen,
)
from utilities.bases.cog import AGBCog
from utilities.embed import Embed
from utilities.functions import fmt_str
from utilities.pagination import Paginator

if TYPE_CHECKING:
    import asyncpg

    from utilities.bases.context import AGBContext


class InventoryPageSource(menus.ListPageSource):
    def __init__(
        self,
        pool: asyncpg.Pool[asyncpg.Record],
        entries: list[InventoryCard],
    ) -> None:
        super().__init__(entries, per_page=1)
        self.pool = pool

    async def format_page(self, _: Paginator, page: InventoryCard) -> Embed:
        card_assets = await page.show(self.pool)

        return Embed(
            title=f'{card_assets.name}',
            description=fmt_str(
                [
                    f'Rarity: {" ".join(rarity_emoji_gen(card_assets.rarity))}',
                    f'Burn Worth: {BURN_WORTH[card_assets.rarity]}',
                    f'Theme: {card_assets.theme}',
                    f'Quantity: {page.quantity}',
                    f'Is locked: {"Yes" if page.locked is True else "No"}',
                    f'ID: {page.id}',
                ],
                seperator='\n',
            ),
            colour=discord.Colour.from_str(RARITY_COLOURS[card_assets.rarity]),
        ).set_image(url=card_assets.image)


class CardsPageSource(menus.ListPageSource):
    def __init__(self, entries: list[Card]) -> None:
        super().__init__(entries, per_page=1)

    async def format_page(self, _: Paginator, page: Card) -> Embed:
        return Embed(
            title=page.name,
            description=fmt_str(
                [
                    f'Rarity: {" ".join(rarity_emoji_gen(page.rarity))}',
                    f'Burn Worth: {BURN_WORTH[page.rarity]}',
                    f'Theme: {page.theme}',
                    f'ID: {page.id}',
                ],
                seperator='\n',
            ),
            colour=discord.Colour.from_str(RARITY_COLOURS[page.rarity]),
        ).set_image(url=page.image)


class GiftFlags(commands.FlagConverter):
    blombos: int | None
    card: str | None


CARD_GIFT_QUERY = """
WITH to_be_gifted AS (
   SELECT id
   FROM   CardInventory
   WHERE  user_id = $1 AND id = $2
   LIMIT  1
   )
UPDATE CardInventory s
SET    user_id = $3
FROM   to_be_gifted
WHERE  s.id = to_be_gifted.id
"""

user_param = commands.parameter(converter=GachaMemberConverter)


class Cards(AGBCog):
    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def inventory(self, ctx: AGBContext, user: discord.Member = commands.Author) -> None:
        data = await self.bot.pool.fetch(
            """
            SELECT
                *
            FROM
                CardInventory
            WHERE
                user_id = $1
                """,
            user.id,
        )

        cards = [
            InventoryCard(
                i['id'],
                i['quantity'],
                locked=i['is_locked'],
                shop_listing_id=i['shop_listing_id'],
                notes=i['notes'],
            )
            for i in data
        ]

        paginate = Paginator(InventoryPageSource(self.bot.pool, cards), ctx=ctx)

        await paginate.start()

    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def cards(self, ctx: AGBContext) -> None:
        data = await self.bot.pool.fetch(
            """
            SELECT
                *
            FROM
                Cards
            """,
        )

        cards = [
            Card(
                i['id'],
                name=i['name'],
                rarity=i['rarity'],
                theme=i['theme'],
                image=i['image_url'],
                is_obtainable=i['is_obtainable'],
            )
            for i in data
        ]

        paginate = Paginator(CardsPageSource(cards), ctx=ctx)

        await paginate.start()

    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def gift(
        self,
        ctx: AGBContext,
        user: discord.Member = user_param,
        *,
        gifts: GiftFlags,
    ) -> discord.Message | None:
        if not gifts.blombos and not gifts.card:
            return await ctx.reply('You are trying to gift nothing.')

        s: list[tuple[bool, str | None, int, int | str]] = []
        # NOTE: The tuple represents Success/Failure, message for failure, type of gift, the entry for the gift

        if gifts.blombos:
            balance: int = await self.bot.pool.fetchval(
                """
                SELECT
                    blombos
                from
                    PlayerData
                WHERE
                    user_id = $1
                """,
                ctx.author.id,
            )

            if balance < gifts.blombos:
                s.append((
                    False,
                    f'You are trying to gift {gifts.blombos} blombos but only have {balance}',
                    1,
                    gifts.blombos,
                ))

            else:
                # Blombotic conditions have been met.

                await self.bot.pool.execute(
                    """
                    INSERT INTO
                        PlayerData (user_id, blombos)
                    VALUES
                        ($1, $2)
                    ON CONFLICT (user_id) DO UPDATE
                    SET
                        blombos = PlayerData.blombos + $2
                    """,
                    user.id,
                    gifts.blombos,
                )

                s.append((True, None, 1, gifts.blombos))

        if gifts.card:
            cards = gifts.card.split(',')

            for card in cards:
                try:
                    card_id = int(card)
                except Exception:
                    s.append((False, f'{card} is not a card.', 2, card))
                else:
                    card_data = await self.bot.pool.fetchrow(
                        """
                        SELECT
                            *
                        FROM
                            CardInventory
                        WHERE
                            user_id = $1
                            AND id = $2
                        """,
                        ctx.author.id,
                        card_id,
                    )
                    if card_data is None:
                        s.append((False, f"You don't own {card_id}", 2, card_id))
                        continue

                    if card_data['is_locked'] is True:
                        s.append((False, f'{card_id} is locked', 2, card_id))
                        continue

                    if card_data['shop_listing_id'] is not None:
                        s.append((False, f'{card_id} is currently listed on your shop', 2, card_id))
                        continue

                    await self.bot.pool.execute(
                        CARD_GIFT_QUERY,
                        ctx.author.id,
                        card_id,
                        user.id,
                    )

                    s.append((True, None, 2, card_id))

        await ctx.reply(
            embed=Embed(
                title='Gifts ' + 'sent' if len([_ for _ in s if _[0] is True]) >= 1 else 'not sent',
                description=fmt_str(
                    [f'- {d[1]}' for d in s if d[0] is False],
                    seperator='\n',
                ),
            ),
        )

        if len([_ for _ in s if _[0] is True]) >= 1:
            embed = Embed(title='Gift recieved')
            desc: list[str] = []
            for entry in s:
                if entry[0] is False:
                    continue

                if entry[2] == 1:
                    desc.append(f'- `{entry[3]}` blombos')

                if entry[2] == 2:
                    desc.append(f'- Card `ID:{entry[3]}`')

            embed.description = fmt_str(desc, seperator='\n')
            await user.send(embed=embed)
        return None

    @commands.hybrid_command()
    async def themes(self, ctx: AGBContext) -> None:
        themes = await self.bot.pool.fetch("""SELECT * FROM Themes""")

        s_list: list[str] = []

        for i, theme in enumerate(themes):
            s_list.append(f'{i}. {theme["name"]}' + ('**[Disabled]**' if theme['is_disabled'] is True else ''))

        embed = Embed(title='Themes', description=fmt_str(s_list, seperator='\n'))

        await ctx.reply(embed=embed)
