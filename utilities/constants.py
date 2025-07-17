from __future__ import annotations

import discord

__ALL__ = (
    'BASE_COLOUR',
    'ERROR_COLOUR',
    'BOT_THRESHOLD',
    'BLACKLIST_COLOUR',
    'BOT_FARM_COLOUR',
    'BotEmojis',
    'WebhookThreads',
)

BASE_COLOUR = discord.Colour.from_str('#A27869')
ERROR_COLOUR = discord.Colour.from_str('#bb6688')

CHAR_LIMIT = 2000


class BotEmojis: ...
