from __future__ import annotations

import asyncio
import contextlib
import io
import platform
from textwrap import dedent, indent
from traceback import format_exc
from typing import TYPE_CHECKING

from discord import Colour, DiscordException, Embed, TextChannel, VoiceChannel
from discord import __version__ as dpy_v
from discord.ext.commands import BucketType, Cog, bot_has_permissions, command, cooldown

from mainbot.core import Context
from mainbot.core.constants import COMMAND_CATEGORIES
from mainbot.core.paginator import Paginator
from mainbot.utils import checks, close, get_logger, restart
from mainbot.utils.util import clean_code

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

logger = get_logger(__name__)


class Developer(Cog):
    r"""Exclusive features for the bot's creator/owner"""

    def __init__(self):
        self.emoji_id = 868414100915499068  # TODO: Change this id with read emoji id

    async def cog_check(self, ctx: Context) -> bool:
        return await ctx.bot.is_owner(ctx.author)

    @command(name="createwebhook", aliases=["cwh"])
    @cooldown(1, 3, BucketType.user)
    async def create_webhook(self, ctx: Context, channel: TextChannel | VoiceChannel):
        """Create a webhook in the given channel"""
        bot_member = ctx.guild.get_member(ctx.bot.user.id)
        webhook = await channel.create_webhook(
            name=bot_member.name, avatar=await bot_member.avatar.read()
        )
        await ctx.reply(f"Created webhook: ||{webhook.id}||")

    @command()
    @cooldown(1, 3, BucketType.user)
    async def restart(self, ctx: Context):
        """Restart the bot"""
        try:
            await ctx.message.delete()
        except DiscordException:
            pass

        msg = await ctx.send(
            embed=Embed(
                color=Colour.brand_red(),
                description=f"***{ctx.cache.emoji.loading}Restarting...***",
            )
        )

        ctx.db.hmset(
            f"guild:{ctx.guild.id}",
            {"restart_msg": msg.id, "restart_channel": msg.channel.id},
        )
        asyncio.create_task(restart(ctx.bot))

    @command(name="taskcount", aliases=["tc"])
    @cooldown(1, 3, BucketType.user)
    async def task_count(self, ctx: Context):
        """
        Return total task count running in background in the bot.
        Use for tracking the load on the bot
        """
        tasks = asyncio.all_tasks()
        filtered_task = [task for task in tasks if not task.done()]
        await ctx.reply(
            embed=Embed(
                color=Colour.random(),
                title="__Background Tasks__",
                description=dedent(
                    f"""\
                > **Total scheduled tasks: `{len(tasks)}`**

                > **Current running tasks in background: `{len(filtered_task)}`**
                """
                ),
            ).set_thumbnail(url=ctx.bot.get_emoji(809890706784649237).url),
            delete_after=None if ctx.channel.category_id in COMMAND_CATEGORIES else 10,
        )

    @command(
        name="logout",
        aliases=["disconnect", "close", "stopbot"],
        description="Disconnect the bot from discord",
    )
    async def logout(self, ctx):
        if checks.is_invoked_with_command(ctx):
            await ctx.reply(f"Hey {ctx.author.mention}, I am now logging out :wave:")
        await close(ctx.bot)

    @command(hidden=True)
    async def leave(self, ctx, guild: int = None):
        if not guild:
            return await ctx.reply("Please enter the guild id")
        guild = ctx.bot.get_guild(guild)
        if not guild:
            return await ctx.reply("I don't recognize that guild")
        await guild.leave()
        await ctx.author.send(f":ok_hand: Left guild: {guild.name} ({guild.id})")

    @command(name="eval", aliases=["exec"], hidden=True)
    @bot_has_permissions(embed_links=True)
    async def eval(self, ctx, *, code):
        code = clean_code(code)
        local_variables = {
            "Embed": Embed,
            "bot": ctx.bot,
            "cache": ctx.cache,
            "db": ctx.db,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
        }
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                exec(f"async def func():\n{indent(code, '    ')}", local_variables)
                obj = await local_variables["func"]()
                result = f"{stdout.getvalue()}\n-- {obj}\n"
        except (Exception, SyntaxError):
            result = "".join(format_exc())
        pages = [result[i : i + 2000] for i in range(0, len(result), 2000)]
        em = []
        for index, page in enumerate(pages):
            em.append(
                Embed(
                    color=Colour.random(), description=f"```py\n{page}\n```"
                ).set_footer(text=f"Page {index}/{len(pages)}")
            )
        await Paginator(ctx.message, em).start()

    @command(name="botstats")
    @cooldown(1, 3, BucketType.user)
    async def stats_bot(self, ctx: Context):
        """
        A useful command that displays bot statistics.
        """
        em = Embed(
            title=f"{ctx.bot.user.name} Stats",
            description="\uFEFF",
            colour=ctx.author.color,
            timestamp=ctx.message.created_at,
        )
        em.add_field(name="Python Version:", value=platform.python_version())
        em.add_field(name="nextcord.Py Version", value=dpy_v)
        em.add_field(name="Total Guilds:", value=str(len(ctx.bot.guilds)))
        em.add_field(
            name="Total Users:", value=str(len(set(ctx.bot.get_all_members())))
        )
        em.add_field(name="Bot Developers:", value=f"<@{ctx.bot.owner_id}>")
        em.set_image(
            url=(
                await ctx.bot.session.get(
                    "https://source.unsplash.com/random/?server,computer,internet"
                )
            ).url
        )
        em.set_author(name=ctx.author.name, icon_url=ctx.author.display_avatar.url)

        await ctx.reply(embed=em)

    @command()
    async def sync(self, ctx: Context):
        """Sync all application commands"""
        await ctx.bot.sync_all_application_commands()
        await ctx.message.add_reaction("✅")

    @command(hidden=True)
    async def test(self, ctx: Context):
        """Test command"""
        await ctx.message.add_reaction("✅")


async def setup(bot: MainBot):
    await bot.add_cog(Developer())
