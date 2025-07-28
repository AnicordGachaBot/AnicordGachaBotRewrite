from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands, menus

from utilities.bases.cog import AGBCog
from utilities.constants import BURN_WORTH, HOLLOW_STAR, RARITY_COLOURS, RARITY_EMOJIS
from utilities.embed import Embed
from utilities.functions import fmt_str
from utilities.pagination import Paginator

if TYPE_CHECKING:
    import asyncpg

    from utilities.bases.context import AGBContext


class InventoryCard:
    def __init__(
        self, id: int, *, locked: bool = False, shop_listing_id: int | None = None, notes: str | None = None
    ) -> None:
        super().__init__()
        self.id = id
        self.locked = locked
        self.shop_listing_id = shop_listing_id
        self.notes = notes

    async def show(self, pool: asyncpg.Pool[asyncpg.Record]) -> asyncpg.Record:
        data = await pool.fetchrow("""SELECT * FROM Cards WHERE id = $1""", self.id)

        if not data:
            raise TypeError('Expected a Record, not None')

        return data


class Card:
    def __init__(
        self,
        id: int,
        *,
        name: str,
        rarity: int,
        theme: str,
        is_obtainable: bool = True,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.rarity = rarity
        self.theme = theme
        self.is_obtainable = is_obtainable


def rarity_emoji_gen(r: int) -> list[str]:
    s: list[str] = [str(HOLLOW_STAR) for _ in range(5 if r != 6 else 6)]

    for rr in range(r):
        s[rr] = str(RARITY_EMOJIS[r])

    return s


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
            title=f'{card_assets["name"]}',
            description=fmt_str(
                [
                    f'Rarity: {" ".join(rarity_emoji_gen(card_assets["rarity"]))}',
                    f'Burn Worth: {BURN_WORTH[card_assets["rarity"]]}',
                    f'Theme: {card_assets["theme"]}',
                    f'ID: {page.id}',
                ],
                seperator='\n',
            ),
            colour=discord.Colour.from_str(RARITY_COLOURS[card_assets['rarity']]),
        )


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
        )


class GiftFlags(commands.FlagConverter):
    blombos: int | None
    card: int | None


class Cards(AGBCog):
    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def inventory(self, ctx: AGBContext, user: discord.User = commands.Author) -> None:
        data = await self.bot.pool.fetch("""SELECT * FROM CardInventory WHERE user_id = $1""", user.id)

        cards = [
            InventoryCard(i['id'], locked=i['is_locked'], shop_listing_id=i['shop_listing_id'], notes=i['notes'])
            for i in data
        ]

        paginate = Paginator(InventoryPageSource(self.bot.pool, cards), ctx=ctx)

        await paginate.start()

    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def cards(self, ctx: AGBContext) -> None:
        data = await self.bot.pool.fetch("""SELECT * FROM Cards""")

        cards = [
            Card(i['id'], name=i['name'], rarity=i['rarity'], theme=i['theme'], is_obtainable=i['is_obtainable'])
            for i in data
        ]

        paginate = Paginator(CardsPageSource(cards), ctx=ctx)

        await paginate.start()

    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def gift(self, ctx: AGBContext, user: discord.User | discord.Member, *, gifts: GiftFlags):
        if user.bot is True:
            return await ctx.reply(
                f'You know..... you can burn the cards instead of gifting it to a bot..... I know you love {user} but man......'
            )

        if user.id == ctx.author.id:
            return await ctx.reply(
                'Alright. Done. Transferred blombos from your account to your account. (May god forgive you cuz I wont)'
            )

        to_be_gifted_blombos = gifts.blombos

        if to_be_gifted_blombos is not None:
            blombos = await self.bot.pool.fetchval("""SELECT blombos FROM PlayerData WHERE user_id = $1""", ctx.author.id)

            if not blombos or int(blombos) < to_be_gifted_blombos:
                return await ctx.reply('You dont have enough blombos')
