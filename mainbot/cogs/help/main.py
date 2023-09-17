from __future__ import annotations

from typing import TYPE_CHECKING

from discord.ext.commands import Cog, Context

from mainbot.utils import checks, get_logger

from .embed_utilizer import EmbedHelpCommand

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)


class Help(Cog, name="Help command", command_attrs=dict(hidden=True)):
    """Displays help information for commands and cogs"""

    def __init__(self, bot: MainBot):
        self.__bot = bot
        self.__original_help_command = bot.help_command
        bot.help_command = EmbedHelpCommand()
        bot.help_command.cog = self

    def cog_unload(self):
        self.__bot.help_command = self.__original_help_command

    async def cog_check(self, ctx: Context):
        return await checks.in_command_channel(ctx)


# setup functions for bot
async def setup(bot: MainBot):
    await bot.add_cog(Help(bot))
