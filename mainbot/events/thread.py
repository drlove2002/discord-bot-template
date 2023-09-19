from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Thread, ThreadMember
from discord.ext.commands import Cog

from mainbot.utils import get_logger

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)


class ThreadHandler(Cog):
    """Handles thread events"""

    def __init__(self, bot: MainBot):
        self.bot = bot

    @Cog.listener()
    async def on_thread_create(self, thread: Thread):
        pass

    @Cog.listener()
    async def on_thread_update(self, before: Thread, after: Thread):
        if after.archived and not before.archived:
            self.bot.dispatch("thread_archived", after)

        if None in (before.applied_tags, after.applied_tags):
            # Thread is not a forum thread
            return

        if tags := (set(before.applied_tags) - set(after.applied_tags)):
            self.bot.dispatch("thread_tag_removed", after, tags.pop())
            return
        if tags := (set(after.applied_tags) - set(before.applied_tags)):
            self.bot.dispatch("thread_tag_added", after, tags.pop())
            return

    @Cog.listener()
    async def on_thread_tag_added(self, thread: Thread, tag: str):
        pass

    @Cog.listener()
    async def on_thread_tag_removed(self, thread: Thread, tag: str):
        pass

    @Cog.listener()
    async def on_thread_archived(self, thread: Thread):
        pass

    @Cog.listener()
    async def on_thread_member_remove(self, thread_member: ThreadMember):
        thread = thread_member.thread

        try:
            del thread._members[thread_member.id]
        except KeyError:
            pass

    @Cog.listener()
    async def on_thread_member_join(self, thread_member: ThreadMember):
        pass


async def setup(bot: MainBot):
    await bot.add_cog(ThreadHandler(bot))
