from __future__ import annotations

import datetime
from typing import TYPE_CHECKING, Any

import discord
from discord.ext import commands

if TYPE_CHECKING:
    import asyncpg
    from asyncpg import Record

    from utilities.bases.context import AGBContext


RARITY_EMOJIS = {
    1: discord.PartialEmoji(id=1259718293410021446, name='RedStar'),
    2: discord.PartialEmoji(id=1259690032554577930, name='GreenStar'),
    3: discord.PartialEmoji(id=1259557039441711149, name='YellowStar'),
    4: discord.PartialEmoji(id=1259718164862996573, name='PurpleStar'),
    5: discord.PartialEmoji(id=1259557105220976772, name='RainbowStar'),
    6: discord.PartialEmoji(id=1259689874961862688, name='BlackStar'),
}
HOLLOW_STAR = discord.PartialEmoji(name='HollowStar', id=1259556949867888660)

BURN_WORTH = {
    1: 5,
    2: 10,
    3: 15,
    4: 20,
    5: 25,
    6: 30,
}

RARITY_COLOURS = {
    1: '#607D8B',
    2: '#206694',
    3: '#992D22',
    4: '#E67E22',
    5: '#9B59B6',
    6: '#FF0062',
}


RARITY_WEIGHTS = {
    1: 0.4395,
    2: 0.4,
    3: 0.1,
    4: 0.05,
    5: 0.01,
    6: 0.0005,
}

PULL_INTERVAL = datetime.timedelta(hours=6)

RARITY_PULL_MESSAGES = {
    1: 'You won a Common Card',
    2: 'Nice! You won an Uncommon Card!',
    3: 'Oooo! You won a Rare Card!!',
    4: "Woah!!! You won a Super Rare Card! You're pretty lucky!",
    5: 'Holycow!!! A Legendary Card!! You hit the Jackpot!!! CONGRATS! \U0001f44f',
    6: "Wait...WHAT!?! This Card doesn't even exist in our Database, HOW DID YOU GET THIS!?",
}


class InventoryCard:
    def __init__(
        self,
        id: int,
        quantity: int,
        *,
        locked: bool = False,
        shop_listing_id: int | None = None,
        notes: str | None = None,
    ) -> None:
        super().__init__()
        self.id = id
        self.quantity = quantity
        self.locked = locked
        self.shop_listing_id = shop_listing_id
        self.notes = notes

    async def show(self, pool: asyncpg.Pool[asyncpg.Record]) -> Card:
        data = await pool.fetchrow(
            """
            SELECT
                *
            FROM
                Cards
            WHERE
                id = $1
            """,
            self.id,
        )

        if not data:
            raise TypeError('Expected a Record, not None')

        return Card(
            data['id'],
            name=data['name'],
            rarity=data['rarity'],
            theme=data['theme'],
            image=data['image_url'],
        )


class Card:
    def __init__(  # noqa: PLR0913
        self,
        id: int,
        *,
        name: str,
        rarity: int,
        theme: str,
        image: str,
        is_obtainable: bool = True,
    ) -> None:
        super().__init__()
        self.id = id
        self.name = name
        self.rarity = rarity
        self.theme = theme
        self.image = image
        self.is_obtainable = is_obtainable

    async def give(self, pool: asyncpg.Pool[asyncpg.Record], *, user: discord.Member | discord.User) -> Record | None:
        return await pool.fetchrow(
            """
            INSERT INTO
                CardInventory (user_id, id, quantity)
            VALUES
                ($1, $2, 1)
            ON CONFLICT (user_id, id) DO
            UPDATE
            SET
                quantity = CardInventory.quantity + 1
            RETURNING
                *
            """,
            user.id,
            self.id,
        )


def rarity_emoji_gen(r: int) -> list[str]:
    s: list[str] = [str(HOLLOW_STAR) for _ in range(5 if r != 6 else 6)]

    for rr in range(r):
        s[rr] = str(RARITY_EMOJIS[r])

    return s


class ThemeConverter(commands.Converter[str]):
    async def convert(self, ctx: AGBContext, argument: str) -> str:
        themes: dict[str, dict[str, Any]] = ctx.bot.gacha_variables['themes']

        if argument.lower() not in [_.lower() for _ in themes]:
            raise commands.BadArgument('This theme does not exist')

        if themes[argument.lower()]['is_disabled'] is True:
            raise commands.BadArgument('This theme is currently disabled')

        return argument


class GachaMemberConverter(commands.MemberConverter):
    async def convert(self, ctx: AGBContext, argument: str) -> discord.Member:
        p = await super().convert(ctx, argument)

        if p.bot is True:
            raise commands.BadArgument('This user is a bot')

        if p.id == ctx.author.id:
            raise commands.BadArgument("The target for this argument can't be you")

        return p
