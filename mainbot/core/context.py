from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext import commands

if TYPE_CHECKING:
    from .bot import MainBot


class Context(commands.Context):
    bot: MainBot

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = self.bot.cache
        self.db = self.bot.db
        self.webhook = self.cache.webhook
        self.extras = {}
