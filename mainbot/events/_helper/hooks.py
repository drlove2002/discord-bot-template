from __future__ import annotations

from asyncio import create_task
from typing import TYPE_CHECKING

from discord import Colour, DiscordException, Embed
from discord.ext.commands import UserInputError

from mainbot.core import Context
from mainbot.core.constants import COMMAND_CATEGORIES
from mainbot.utils import close, get_logger

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)

__all__ = (
    "setup",
    "after_cmd_invoke",
    "before_cmd_invoke",
)


async def setup(bot: MainBot) -> None:
    """A function that is called when the bot is ready for further setup."""
    import signal

    from discord import Activity, ActivityType, Status

    await bot.change_presence(
        activity=Activity(
            type=ActivityType.watching,
            name=f"Watching {len(set(bot.get_all_members()))} people",
        ),
        status=Status.online,
    )

    # Load restart configs from db
    key = f"guild:{bot.guild().id}"
    if bot.db.hexists(key, "restart_msg"):
        msg = await bot.get_channel(
            int(bot.db.hget(key, "restart_channel"))
        ).fetch_message(int(bot.db.hget(key, "restart_msg")))
        create_task(
            msg.edit(
                embed=Embed(
                    color=Colour.green(),
                    description="***✅ Restarted!***",
                )
            )
        )
        bot.db.hdel(key, "restart_msg", "restart_channel")

    if bot.test:
        return

    # Add signal handlers
    for sig in (signal.SIGTERM, signal.SIGINT):
        bot.loop.remove_signal_handler(sig)
        bot.loop.add_signal_handler(sig, lambda: create_task(close(bot)))


async def after_cmd_invoke(ctx: Context):
    """A function that is called after every command invocation."""
    delay = ctx.command.extras.get("delete_delay", 0)
    if ctx.channel.category_id in COMMAND_CATEGORIES or not delay:
        return
    try:
        await ctx.message.delete(delay=delay)
    except DiscordException:
        pass


async def before_cmd_invoke(ctx: Context):
    """A function that is called before every command invocation."""
    if (
        ctx.channel.category_id == 805206345212624896  # TODO: Change with real ids
        and ctx.channel.id == 805206389889826866  # TODO: Change with real ids
    ):
        raise UserInputError("You can't use commands in this channel")
