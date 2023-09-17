from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Member, Role
from discord.abc import GuildChannel
from discord.ext.commands import Cog

from mainbot.utils import get_logger

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)


class MemberHandler(Cog):
    """Handles member events"""

    def __init__(self, bot: MainBot):
        self.bot = bot
        self.db = bot.db
        self.guild = bot.guild

    @Cog.listener()
    async def on_member_join(self, member: Member):
        pass

    @Cog.listener()
    async def on_member_remove(self, member: Member):
        pass

    @Cog.listener()
    async def on_presence_update(self, before: Member, after: Member):
        if after.status != before.status:
            self.bot.dispatch("status_update", after)
            return

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        if after.bot:
            return
        if before.pending and not after.pending:
            self.bot.dispatch("verified", after)
            return

        for old_role in set(before._roles).difference(set(after._roles)):
            self.bot.dispatch("role_removed", after, after.guild.get_role(old_role))
            return

        for new_role in set(after._roles).difference(set(before._roles)):
            self.bot.dispatch("role_added", after, after.guild.get_role(new_role))
            return

    @Cog.listener()
    async def on_status_update(self, member: Member):
        pass

    @Cog.listener()
    async def on_guild_channel_delete(self, channel: GuildChannel):
        pass

    @Cog.listener()
    async def on_role_removed(self, member: Member, role: Role):
        pass

    @Cog.listener()
    async def on_role_added(self, member: Member, role: Role):
        pass


async def setup(bot: MainBot):
    await bot.add_cog(MemberHandler(bot))
