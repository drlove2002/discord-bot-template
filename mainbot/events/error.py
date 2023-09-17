from discord import DiscordException
from discord.ext.commands import (
    BotMissingPermissions,
    Cog,
    CommandError,
    CommandInvokeError,
    CommandOnCooldown,
    ConversionError,
    MaxConcurrencyReached,
    MissingPermissions,
    MissingRole,
    UserInputError,
)

from mainbot.core import Context
from mainbot.core.constants import COMMAND_CATEGORIES
from mainbot.utils import Raise, humanize_time

N = "on_command_error"


class ErrorHandler(Cog):
    @Cog.listener(name=N)
    async def missing_perms(self, ctx: Context, error: Exception):
        if not isinstance(error, (MissingPermissions, BotMissingPermissions)):
            return
        missing_perms = ", ".join(error.missing_permissions)
        msg = "You are" if isinstance(error, MissingPermissions) else "I am"
        await Raise(ctx, f"{msg} missing: `{missing_perms}` to run this command").info()

    @Cog.listener(name=N)
    async def concurrency_error(self, ctx: Context, error: Exception):
        if not isinstance(error, MaxConcurrencyReached):
            return
        if error.per.name == "user":
            await Raise(
                ctx,
                f"You are already using `{ctx.command.name.capitalize()}` Command, wait until you finish!",
            ).info()
            return
        await Raise(
            ctx,
            f"Someone is already using `{ctx.command.name.capitalize()}` Command, wait until they finish!",
        ).info()

    @Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        if ctx.channel.category_id not in COMMAND_CATEGORIES:
            try:
                await ctx.message.delete(delay=2)
            except DiscordException:
                pass

        if isinstance(
            error,
            (
                ConversionError,
                UserInputError,
                MissingRole,
            ),
        ):
            if str(error):
                await Raise(ctx, str(error)).info()
            ctx.command.reset_cooldown(ctx)
        if hasattr(error, "original") and str(error.original).startswith("[Errno 104]"):
            await Raise(ctx, "I am having trouble connecting to the internet").info()
            ctx.command.reset_cooldown(ctx)
            return

        if not isinstance(error, CommandInvokeError):  # Ignore these errors
            return
        try:
            await Raise(
                ctx.webhook.log,
                f"`{ctx.channel.mention} {ctx.author.name} \n {str(error.original)}`",
            ).error()
        except TypeError:
            pass
        raise error

    @Cog.listener(name=N)
    async def command_on_cooldown(self, ctx: Context, error: Exception):
        if not isinstance(error, CommandOnCooldown):
            return
        # If the command is currently on cooldown trip this
        await Raise(ctx, f"Cooldown: `{humanize_time(error.retry_after)}`").info()


async def setup(bot):
    await bot.add_cog(ErrorHandler())
