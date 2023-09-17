from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import BucketType, Cog, cooldown, hybrid_command

from mainbot.core import Context

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot


class Mics(Cog, name="Miscellaneous"):
    """Collect items and use them to get rewards"""

    thumbnail = "https://cdn-icons-png.flaticon.com/512/6299/6299644.png"

    def __init__(self):
        self.emoji_id = 868414100915499068  # TODO: Change this id with read emoji id

    @hybrid_command()
    @cooldown(1, 3, BucketType.guild)
    async def ping(self, ctx: Context):
        """See how fast I can response"""
        await ctx.send(f"> Pong! `{round(ctx.bot.latency * 1000)}ms`")


async def setup(bot: MainBot):
    await bot.add_cog(Mics())
