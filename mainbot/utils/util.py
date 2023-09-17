import re
from datetime import datetime, timedelta
from typing import NamedTuple

from discord import (
    AllowedMentions,
    Colour,
    DiscordException,
    Embed,
    Interaction,
    Message,
    Webhook,
)
from discord.ext.commands import Context

from mainbot.core.constants import ALPHABETS, COMMAND_CATEGORIES, NORMALIZE_CHARS

__all__ = (
    "clean",
    "clean_code",
    "code_block",
    "humanize_time",
    "daily_time",
    "weekly_time",
    "Raise",
)


def clean(message: Message | str) -> str:
    if isinstance(message, Message):
        text = message.content
        for m in set(message.mentions):
            text = text.replace(m.mention, m.name)
    else:
        text = message
    unique = [
        i for i in set(text) if i not in ALPHABETS[0]
    ]  # handle special chars from other langs
    for _char in unique:
        try:
            text = text.replace(_char, NORMALIZE_CHARS[_char])
        except KeyError:
            pass
    text = re.sub(
        re.compile(
            r"[\U00003000\U0000205F\U0000202F\U0000200A\U00002000-\U00002009\U00001680\U000000A0\t]+"
        ),
        " ",
        text,
    )  # handle... interesting spaces
    text = re.sub(
        re.compile(r'([.\'"@?!a-z])\1{4,}', re.IGNORECASE), r"\1\1\1", text
    )  # handle excessive repeats of punctuation, limited to 3
    text = re.sub(
        re.compile(r"\s(.+?)\1+\s", re.IGNORECASE), r" \1 ", text
    )  # handle repeated words
    text = re.sub(
        re.compile(r'([\s!?@"\'])\1+'), r"\1", text
    )  # handle excessive spaces or excessive punctuation
    text = re.sub(
        re.compile(r"\s([?.!\"](?:\s|$))"), r"\1", text
    )  # handle spaces before punctuation but after text
    text = text.strip().replace("\n", "/n")  # handle newlines
    text = text.encode("ascii", "ignore").decode()  # remove all non-ascii
    text = text.strip()  # strip the line
    return text


def clean_code(content):
    if content.startswith("```") and content.endswith("```"):
        return "\n".join(content.split("\n")[1:])[:-3]
    else:
        return content


def code_block(content, lang=""):
    return f"```{lang}\n{content}\n```"


def humanize_time(dt: timedelta | float = None):
    """Convert a timedelta or seconds to a human-readable string"""

    def format_data(_time: int, word: str):
        return f"{_time} {word}{'s' if _time > 1 else ''}"

    if dt is None:
        dt = timedelta(seconds=0)
    elif isinstance(dt, (float, int)):
        dt = timedelta(seconds=dt)
    d = dt.days
    m, s = divmod(dt.seconds, 60)
    h, m = divmod(m, 60)
    if int(d):
        return f"{format_data(int(d), 'Day')}, {format_data(int(h), 'Hour')}"
    elif int(h):
        return f"{format_data(int(h), 'Hour')}, {m} Min"
    elif int(m):
        return f"{m} Min, {s} Sec"
    else:
        if s < 1:
            s = dt.total_seconds()
            if s < 0.1:
                return f"{s} Sec"
            else:
                return f"{round(s, 1)} Sec"
        else:
            return f"{int(s)} Sec"


def daily_time() -> datetime:
    now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    return now + timedelta(hours=24 - now.hour)


def weekly_time() -> datetime:
    now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    return now + timedelta(days=7 - now.weekday())


class RaiseType(NamedTuple):
    emoji: str
    color: Colour


class Raise:
    def __init__(
        self,
        ctx: Context | Interaction | Message | Webhook,
        message: str,
        *,
        delete_after: int | float | None = 10,
        edit: Message | bool | None = False,
        ephemeral=True,
        view=None,
    ):
        self.ctx = ctx
        self.msg = message
        self.view = view
        self.del_after = (
            None if ctx.channel.category_id in COMMAND_CATEGORIES else delete_after
        )
        self.edit = edit
        self.ephemeral = ephemeral

    async def __response(self, emoji_dict: RaiseType) -> Message | None:
        allowed_mentions = AllowedMentions(
            everyone=False, users=True, roles=False, replied_user=True
        )
        em = Embed(
            color=emoji_dict.color, description=f"{emoji_dict.emoji}**{self.msg}**"
        )
        if isinstance(self.ctx, Interaction):
            if self.edit:
                if isinstance(self.edit, Message):
                    return await self.edit.edit(embed=em, view=self.view)
                return await self.ctx.edit_original_response(embed=em, view=self.view)
            return await self.ctx.response.send_message(
                embed=em, ephemeral=self.ephemeral, allowed_mentions=allowed_mentions
            )

        elif isinstance(self.ctx, Message):
            try:
                if self.view is not None:
                    raise DiscordException
                return await self.ctx.reply(
                    embed=em,
                    delete_after=self.del_after,
                    allowed_mentions=allowed_mentions,
                    view=self.view,
                )
            except DiscordException:
                return await self.ctx.channel.send(
                    self.ctx.author.mention,
                    embed=em,
                    delete_after=self.del_after,
                    allowed_mentions=allowed_mentions,
                    view=self.view,
                )
        elif isinstance(self.ctx, Webhook):
            return await self.ctx.send(embed=em, view=self.view)
        else:
            if self.edit:
                return await self.edit.edit(
                    content=self.ctx.author.mention,
                    embed=em,
                    delete_after=self.del_after,
                    view=self.view,
                    allowed_mentions=allowed_mentions,
                )
            try:
                if self.ctx.message.author.bot or self.del_after:
                    raise DiscordException
                return await self.ctx.reply(
                    embed=em, allowed_mentions=allowed_mentions, view=self.view
                )
            except DiscordException:
                return await self.ctx.send(
                    self.ctx.author.mention,
                    embed=em,
                    delete_after=self.del_after,
                    view=self.view,
                    allowed_mentions=allowed_mentions,
                )

    async def error(self) -> Message | None:
        return await self.__response(
            RaiseType("<a:alert:1152907495191351316> ", Colour.red())
        )

    async def info(self) -> Message | None:
        return await self.__response(
            RaiseType("<a:crossmark:1152907598899728395>", Colour.yellow())
        )

    async def success(self) -> Message | None:
        return await self.__response(
            RaiseType("<a:check:1152908387462426774>", Colour.green())
        )

    async def loading(self) -> Message | None:
        return await self.__response(
            RaiseType("<a:loading:1152863463476047874>", Colour.blurple())
        )

    async def custom(self, emoji: str, color: Colour) -> Message | None:
        return await self.__response(RaiseType(emoji, color))
