from __future__ import annotations

import contextlib

import discord

__all__ = ('BaseView',)


class BaseView(discord.ui.View):
    message: discord.Message | None

    def __init__(self, *, timeout: float = 180.0) -> None:
        super().__init__(timeout=timeout)

    async def on_timeout(self) -> None:
        with contextlib.suppress(discord.errors.NotFound):
            if hasattr(self, 'message') and self.message:
                await self.message.edit(view=None)
        self.stop()
