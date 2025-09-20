from __future__ import annotations

from typing import TYPE_CHECKING

from extensions.anicord_gacha.cards import Cards
from extensions.anicord_gacha.gacha import Gacha
from extensions.anicord_gacha.leaderboard import Leaderboard
from extensions.anicord_gacha.profile import Profile

if TYPE_CHECKING:
    from utilities.bases.bot import AnicordGachaBot


class AnicordGacha(Cards, Profile, Leaderboard, Gacha, name='AnicordGacha'): ...


async def setup(bot: AnicordGachaBot) -> None:
    await bot.add_cog(AnicordGacha(bot))
