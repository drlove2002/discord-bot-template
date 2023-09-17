# Standard libraries
import os
import sys
import traceback
from pathlib import Path
from typing import TypeVar

# Third party libraries
import aiohttp
from discord.ext import tasks

from . import Cache

try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except ImportError:
    pass
from discord import (
    Activity,
    ActivityType,
    Guild,
    Intents,
    Message,
    NotFound,
    Object,
    Status,
)
from discord import __version__ as dpy_v
from discord.ext.commands import Bot, Cog, ExtensionAlreadyLoaded, when_mentioned_or

# Local code
from mainbot import __version__
from mainbot.events import after_cmd_invoke, before_cmd_invoke, setup
from mainbot.utils import RedisClient, get_logger, load_cogs, load_events

from .context import Context
from .views import add_persistent_items

ROOT_DIR = str(Path(__file__).parents[1])
logger = get_logger(__name__)
logger.info(f"{ROOT_DIR}\n-----")

__all__ = ("BaseMainBot", "MainBot")


class BaseMainBot(Bot):
    def __init__(self):
        self.test: bool = os.getenv("TEST", "False").lower() in ("1", "true", "T")
        super().__init__(
            intents=Intents._from_value(
                2134923
            ),  # TODO: Change the intents as per needed
            command_prefix="$" if self.test else "!",
            case_insensitive=True,
            strip_after_prefix=True,
            activity=Activity(type=ActivityType.playing, name="Loading... 🔄"),
            status=Status.idle,
        )
        # Defining a few things
        self.session = aiohttp.ClientSession(trust_env=True)
        self.db = RedisClient()
        self.cache = Cache()
        self.after_invoke(after_cmd_invoke)
        self.before_invoke(before_cmd_invoke)

    def guild(self) -> Object | Guild:
        get_guild = self.get_guild if self.is_ready() else Object
        # TODO: Change the guild ids to your guild id and test guild id
        if self.test:
            return get_guild(777131049036546078)
        return get_guild(828966079472205864)

    async def on_error(self, event_method, *args, **kwargs):
        """Called when an error occurs while processing an event."""
        # check if the error is due to not found
        if len(args) > 1 and isinstance(getattr(args[1], "original", None), NotFound):
            # print the the missing object's name
            print(f"[{args[1].original.text}]: {args[1].original.response.url}")
        else:
            print(f"Ignoring exception in {event_method}", file=sys.stderr)
        traceback.print_exc()

    def get_cog(self, name: str) -> Cog | None:
        """Get a cog by name."""
        cog = super().get_cog(name)
        if cog is None:
            for cog_name in self.cogs.keys():
                if (
                    cog_name.lower() == name.lower()
                    or cog_name.lower().removesuffix("s") == name.lower()
                ):
                    return self.cogs[cog_name]
        return cog

    async def setup_hook(self) -> None:
        # Add cogs to the bot
        await load_cogs(self)

        if self.test:
            self.tree.copy_global_to(guild=self.guild())
            await self.tree.sync(guild=self.guild())
            try:
                await self.load_extension("mainbot.events.error")
            except ExtensionAlreadyLoaded:
                pass
            return

        self.one_min_check.start()
        await self.tree.sync()
        await load_events(self)
        add_persistent_items(self)

    async def on_ready(self):
        await setup(self)
        await self.cache.init(self)

        logger.info(f"{len(self.persistent_views)} view(s) are added")
        logger.info(f"Logged in as: {self.user.name} : {self.user.id}")
        logger.line()
        logger.info("Discord.py: v%s", dpy_v)
        logger.info("Bot Version: %s", __version__)
        logger.line()

    @tasks.loop(seconds=60)  # task runs every 60 seconds
    async def one_min_check(self):
        pass

    @one_min_check.before_loop
    async def before_my_task(self):
        await self.wait_until_ready()  # wait until the bot logs in

    async def on_message(self, message: Message):
        if message.author.bot or not message.guild:
            return
        await self.process_commands(message)

    async def get_prefix(self, message) -> list[str]:
        return when_mentioned_or(self.command_prefix)(self, message)

    async def get_context(self, message: Message, *, cls=Context):
        return await super().get_context(message, cls=cls)


MainBot = TypeVar("MainBot", bound=BaseMainBot)
"MainBot will be used only for typehints of BaseMainBot"
