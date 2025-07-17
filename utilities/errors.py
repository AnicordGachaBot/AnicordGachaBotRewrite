from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from datetime import datetime


__all__ = (
    'AlreadyBlacklistedError',
    'FeatureDisabledError',
    'MafuyuError',
    'NotBlacklistedError',
    'UnderMaintenanceError',
)


class MafuyuError(discord.ClientException): ...


class FeatureDisabledError(commands.CheckFailure, MafuyuError):
    def __init__(self) -> None:
        super().__init__('This feature is not enabled in this server.')


class AlreadyBlacklistedError(MafuyuError):
    def __init__(
        self,
        snowflake: discord.User | discord.Member | discord.Guild,
        *,
        reason: str,
        until: datetime | None,
    ) -> None:
        self.snowflake = snowflake
        self.reason = reason
        self.until = until
        timestamp_wording = f'until {until}' if until else 'permanently'
        string = f'{snowflake} is already blacklisted for {reason} {timestamp_wording}'
        super().__init__(string)


class NotBlacklistedError(MafuyuError):
    def __init__(self, snowflake: discord.User | discord.Member | discord.Guild | int) -> None:
        self.snowflake = snowflake
        super().__init__(f'{snowflake} is not blacklisted.')


class UnderMaintenanceError(commands.CheckFailure, MafuyuError):
    def __init__(self) -> None:
        super().__init__('The bot is currently under maintenance.')


# TODO(Depreca1ed): All of these are not supposed to be CommandError. Change them to actual errors
