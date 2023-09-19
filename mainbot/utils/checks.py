"""The permission system of the bot is based on a "just works" basis
You have permissions and the bot has permissions. If you meet the permissions
required to execute the command (and the bot does as well) then it goes through
and you can execute the command.
Certain permissions signify if the person is a moderator (Manage Server) or an
admin (Administrator). Having these signify certain bypasses.
Of course, the owner will always be able to execute commands."""
from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING

from discord import DiscordException, DMChannel, Message, Thread
from discord.ext.commands import check

from .util import Raise

if TYPE_CHECKING:
    from discord import TextChannel, VoiceState

    from mainbot.core import Context


async def check_permissions(ctx: Context, perms, *, checks=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    resolved = ctx.channel.permissions_for(ctx.author)
    return checks(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_permissions(*, checks=all, **perms):
    async def pred(ctx):
        return await check_permissions(ctx, perms, checks=checks)

    return check(pred)


def is_invoked_with_command(ctx: Context | Message):
    """Check if the command was invoked bt user or from other commands"""
    if isinstance(ctx, Message):
        return False
    return ctx.valid and ctx.invoked_with in (*ctx.command.aliases, ctx.command.name)


async def check_guild_permissions(ctx, perms, *, checks=all):
    is_owner = await ctx.bot.is_owner(ctx.author)
    if is_owner:
        return True

    if ctx.guild is None:
        return False

    resolved = ctx.author.guild_permissions
    return checks(
        getattr(resolved, name, None) == value for name, value in perms.items()
    )


def has_guild_permissions(*, checks=all, **perms):
    async def pred(ctx):
        return await check_guild_permissions(ctx, perms, checks=checks)

    return check(pred)


# These do not take channel overrides into account


def can_bot(perm: str, ctx: Context, channel: TextChannel | None = None) -> bool:
    channel = channel or ctx.channel
    return isinstance(channel, DMChannel) or getattr(
        channel.permissions_for(ctx.guild.me), perm
    )


def can_send(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("send_messages", ctx, channel)


def can_embed(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("embed_links", ctx, channel)


def can_upload(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("attach_files", ctx, channel)


def can_react(ctx: Context, channel: TextChannel | None = None) -> bool:
    return can_bot("add_reactions", ctx, channel)


async def not_in_thread(ctx: Context) -> bool:
    if not isinstance(ctx.channel, Thread):
        return True
    if is_invoked_with_command(ctx):
        await Raise(ctx, "This command is not allowed in thread").info()
    return False


async def is_channel_active(channel: TextChannel) -> bool:
    messages = [m async for m in channel.history(limit=5)]
    return messages[0].created_at - messages[4].created_at <= timedelta(minutes=2)


def is_in_guilds(*guild_ids):
    def predicate(ctx):
        guild = ctx.guild
        if guild is None:
            return False
        return guild.id in guild_ids

    return check(predicate)


def in_dm(ctx: Context):
    return not ctx.guild


def vc_join(b: VoiceState, a: VoiceState) -> bool:
    """Member joined the VC"""
    return a.channel != b.channel and b.channel is None


def vc_leave(b: VoiceState, a: VoiceState) -> bool:
    """Member joined the VC"""
    return vc_join(a, b)


async def in_command_channel(ctx: Context, *, in_thread: bool = False) -> bool:
    if in_thread and isinstance(ctx.channel, Thread):
        return True
    if ctx.channel == ctx.cache.channel.command:
        return True
    if is_invoked_with_command(ctx):
        await Raise(
            ctx,
            "Only usable in command channels",
            delete_after=5,
        ).info()
        try:
            await ctx.message.delete()
        except DiscordException:
            pass
    return False


def bot_warning(message: Message) -> bool:
    emojis = ("<a:alert:1152907495191351316>", "<a:crossmark:1152907598899728395>")
    return (
        message.author == message.guild.me
        and message.embeds
        and message.embeds[0].description
        and any([message.embeds[0].description.startswith(emoji) for emoji in emojis])
    )
