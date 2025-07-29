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


class BotEmojis:
    GREY_TICK = discord.PartialEmoji(name='grey_tick', id=1278414780427796631)
    GREEN_TICK = discord.PartialEmoji(name='greentick', id=1297976474141200529, animated=True)
    RED_CROSS = discord.PartialEmoji(name='redcross', id=1315758805585498203, animated=True)

    STATUS_ONLINE = discord.PartialEmoji(name='status_online', id=1328344385783468032)

    PASS = discord.PartialEmoji(name='PASS', id=1339697021942108250)
    SMASH = discord.PartialEmoji(name='SMASH', id=1339697033589559296)

    ON_SWITCH = discord.PartialEmoji(name='on_switch', id=1392183715420966963)
    OFF_SWITCH = discord.PartialEmoji(name='off_switch', id=1392183726569685034)

    SLASH = discord.PartialEmoji(name='slash', id=1352388308046581880)


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
