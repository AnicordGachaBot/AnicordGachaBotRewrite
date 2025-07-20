from __future__ import annotations

from extensions.gacha.inventory import Inventory
from utilities.bases.bot import Mafuyu


class Gacha(Inventory, name='Inventory'): ...


async def setup(bot: Mafuyu) -> None:
    await bot.add_cog(Gacha(bot))
