from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from discord import Activity, ActivityType, Status
from discord.ext.commands import ExtensionAlreadyLoaded

from . import logging

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot


logger = logging.get_logger(__name__)
ROOT_DIR = str(Path(__file__).parents[1])

__all__ = (
    "run_command",
    "restart",
    "close",
    "load_cogs",
    "load_events",
)


def run_command(command: str) -> str:
    process = subprocess.Popen(
        command.split(), stdout=subprocess.PIPE, text=True, shell=True
    )
    process.wait()
    output = process.communicate()[0]
    return output


async def restart(bot: MainBot) -> None:
    logger.line()
    await bot.change_presence(
        status=Status.idle,
        activity=Activity(type=ActivityType.watching, name="and Restarting...⚠️"),
    )
    run_command("docker restart bot")
    logger.info("↻ Restarting bot...")
    await close(bot)


async def close(bot: MainBot) -> None:
    """Close the bot gracefully"""
    import asyncio

    # Cancel all tasks
    for task in asyncio.all_tasks():
        task.cancel("Bot is logging out")
    await bot.session.close()
    await bot.close()
    bot.db.close()
    bot.loop.stop()


async def load_cogs(bot: MainBot) -> None:
    """Add all cogs to the bot."""
    for file in os.listdir(ROOT_DIR + "/cogs"):
        if file.startswith("_"):
            continue
        try:
            if os.path.isdir(ROOT_DIR + "/cogs" + f"/{file}"):
                await bot.load_extension(f"mainbot.cogs.{file}.main")
            else:
                file = file[:-3]
                await bot.load_extension(f"mainbot.cogs.{file}")
        except ExtensionAlreadyLoaded:
            pass
        logger.info("✅ %s cog loaded", file.capitalize())
    logger.line()


async def load_events(bot: MainBot) -> None:
    """Add event handlers to the bot"""
    for file in os.listdir(ROOT_DIR + "/events"):
        if file.startswith("_"):
            continue
        try:
            await bot.load_extension(f"mainbot.events.{file[:-3]}")
        except ExtensionAlreadyLoaded:
            pass
