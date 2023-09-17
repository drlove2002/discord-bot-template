from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Member
from discord.ext.commands import MemberConverter

from mainbot.core import Context

if TYPE_CHECKING:
    ReferredUser = Member
else:

    class ReferredUser(MemberConverter):
        """Converts to a member or the author of the referenced message"""

        async def convert(self, ctx: Context, argument: str) -> Member:
            refer = ctx.message.reference
            if refer is not None:
                return refer.resolved.author
            else:
                return await super().convert(ctx, argument)
