from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import asyncpg


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
