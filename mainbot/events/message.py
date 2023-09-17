from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ChannelType, DiscordException, Message
from discord.ext.commands import Cog

from mainbot.utils import get_logger

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)


class MessageHandler(Cog):
    def __init__(self, bot: MainBot):
        self._bot = bot
        self.db = bot.db
        self.guild = bot.guild
        self.cache = bot.cache

    @Cog.listener()
    async def on_message(self, message: Message):
        if not self._bot.is_ready():
            return
        if self._bot.test and (
            (
                message.channel.parent_id
                if message.channel.type
                in (ChannelType.public_thread, ChannelType.private_thread)
                else message.channel.id
            )
            != self.cache.channel.dev_chat
        ):
            return

        if not message.guild:
            self._bot.dispatch("dm_message", message)
            return

        if message.author.bot:
            return

    @Cog.listener()
    async def on_bot_mention(self, message: Message):
        try:
            await message.delete()
        except DiscordException:
            pass

        await message.channel.send(
            f":eyes: My prefix here is `{self._bot.command_prefix}`", delete_after=10
        )


async def setup(bot: MainBot):
    await bot.add_cog(MessageHandler(bot))
