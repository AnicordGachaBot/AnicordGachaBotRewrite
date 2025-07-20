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

RARITY_COLOURS = {1: '#FF0000', 2: '#00FF00', 3: '#FFFF00', 4: '#800080', 5: '#FFFFFF', 6: '#000000'}
