from __future__ import annotations

import asyncio
from collections import deque
from typing import TYPE_CHECKING

from discord import TextChannel, Webhook

from mainbot.utils import get_logger

from .constants import Channel, Emoji, Role

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)


class Cache:
    def __init__(self):
        self.role: Role | None = None
        self.channel: Channel | None = None
        self.emoji: Emoji | None = None
        self.webhook = WHook(self)

    async def init(self, bot: MainBot):
        await bot.wait_until_ready()
        if not bot.guilds:
            await asyncio.sleep(1)
            await self.init(bot)
            return
        self.role = Role(bot)
        self.channel = Channel(bot)
        self.emoji = Emoji(bot)
        await self.webhook.load(bot)


class WHook:
    """Represents Discord Webhooks"""

    def __init__(self, cache: Cache):
        self.cache = cache
        self._hooks: dict[int : deque[Webhook]] = {}

    @property
    def log(self) -> Webhook:
        return self._get_hook(self.cache.channel.log)

    def _get_hook(self, channel: TextChannel) -> Webhook:
        """Get a webhook from the cache"""
        hook = self._hooks[channel].popleft()
        self._hooks[channel].append(hook)
        return hook

    async def load(self, bot: MainBot):
        """Load webhooks into the cache"""
        self._hooks = {
            self.cache.channel.log: deque(),  # log
        }
        for _ in range(3):
            try:
                if bot.test:
                    hook = [
                        w
                        for w in await self.cache.channel.log.webhooks()
                        if w.name == bot.user.name
                    ]
                    for c in self._hooks.keys():
                        self._hooks[c].extend(hook)
                else:
                    for c in self._hooks.keys():
                        self._hooks[c].extend(
                            w for w in await c.webhooks() if w.name == bot.user.name
                        )
                break
            except AttributeError:
                await asyncio.sleep(1)
        logger.info("Loaded webhooks into cache")
