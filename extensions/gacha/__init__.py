from __future__ import annotations

from typing import TYPE_CHECKING

from extensions.gacha.blombos import Blombos
from extensions.gacha.cards import Cards
from extensions.gacha.leaderboard import Leaderboard

if TYPE_CHECKING:
    from utilities.bases.bot import AnicordGachaBot


class Gacha(Cards, Blombos, Leaderboard, name='Gacha'): ...


async def setup(bot: AnicordGachaBot) -> None:
    await bot.add_cog(Gacha(bot))
