from __future__ import annotations

import asyncpg
import discord
from discord.ext import commands, menus

from utilities.bases.cog import MafuCog
from utilities.bases.context import MafuContext
from utilities.constants import BURN_WORTH, HOLLOW_STAR, RARITY_COLOURS, RARITY_EMOJIS
from utilities.embed import Embed
from utilities.functions import fmt_str
from utilities.pagination import Paginator


class Card:
    def __init__(self, id: int, *, locked: bool = False, shop_listing_id: int | None = None, notes: str | None = None):
        self.id = id
        self.locked = locked
        self.shop_listing_id = shop_listing_id
        self.notes = notes

    async def show(self, pool: asyncpg.Pool[asyncpg.Record]):
        data = await pool.fetchrow("""SELECT * FROM Cards WHERE id = $1""", self.id)

        if not data:
            raise TypeError('Expected a Record, not None')

        return data


def rarity(r: int):
    s: list[str] = [str(HOLLOW_STAR) for _ in range(5 if r != 6 else 6)]

    for rr in range(r):
        s[rr] = str(RARITY_EMOJIS[r])

    return s


class InventoryPageSource(menus.ListPageSource):
    def __init__(self, pool: asyncpg.Pool[asyncpg.Record], entries: list[Card]):
        super().__init__(entries, per_page=1)
        self.pool = pool

    async def format_page(self, _: Paginator, page: Card):
        card_assets = await page.show(self.pool)

        embed = Embed(
            title=f'{card_assets["name"]}',
            description=fmt_str(
                [
                    f'Rarity: {" ".join(rarity(card_assets["rarity"]))}',
                    f'Burn Worth: {BURN_WORTH[card_assets["rarity"]]}',
                    f'Theme: {card_assets["theme"]}',
                    f'ID: {page.id}',
                ],
                seperator='\n',
            ),
            colour=discord.Colour.from_str(RARITY_COLOURS[card_assets['rarity']]),
        )

        return embed


class Inventory(MafuCog):
    @commands.hybrid_command()
    @discord.app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @discord.app_commands.allowed_installs(guilds=True, users=True)
    async def inventory(self, ctx: MafuContext, user: discord.User = commands.Author):
        inventory = await self.bot.pool.fetch("""SELECT * FROM CardInventory WHERE user_id = $1""", user.id)

        cards = [
            Card(i['id'], locked=i['is_locked'], shop_listing_id=i['shop_listing_id'], notes=i['notes']) for i in inventory
        ]

        paginate = Paginator(InventoryPageSource(self.bot.pool, cards), ctx=ctx)

        await paginate.start()
