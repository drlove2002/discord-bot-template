from random import randint
from textwrap import dedent

from discord import Embed, SelectOption, ui
from discord.ext import commands
from discord.ext.commands import Cog, UserInputError
from discord.utils import as_chunks

from mainbot.core import Context
from mainbot.core.constants import COMMAND_CATEGORIES, STAFF_CHANNELS
from mainbot.core.paginator import Paginator
from mainbot.utils import Raise

from .views import SelectCog, SelectCommand


class EmbedHelpCommand(commands.HelpCommand):
    """This is an HelpCommand that utilizes embeds."""

    context: Context

    reply = "<:reply:1152942069648732251>"

    def __init__(self):
        super().__init__(
            command_attrs={"hidden": True, "aliases": ["h", "commands", "cmds"]}
        )
        self.per_page_items = 5

    def get_command_signature(self, command):
        return "{0.qualified_name} {0.signature}".format(command)

    def get_cog_emoji(self, cog):
        return self.context.bot.get_emoji(cog.emoji_id) if cog.emoji_id else "📁"

    @staticmethod
    def get_command_description(command):
        return (
            command.description or command.short_doc or command.help or "No Description"
        )

    async def send_error_message(self, error: str):
        if "No command called" in error:
            error = f"Command or category not found. Use `{self.context.prefix}help`"
        await Raise(self.context, error).error()

    # noinspection PyProtectedMember
    def get_command_help(self, command) -> Embed:
        return Embed(
            title=f"Command: {command.name}",
            description=dedent(
                f"""\
            **:bulb: Description**
            ```md
            {(command.callback.__doc__ or "No Description").strip() }
            ```
            **:video_game: Usage**: `{self.context.prefix}{command.name} {command.signature or ''}`\n
            {f"**🦾 Aliases**: `{', '.join(command.aliases)}`" or ""}
            """
            ),
            colour=self.context.author.colour,
        )

    async def get_cog_help(self, cog: Cog) -> tuple[list[Embed], SelectCommand]:
        ctx = self.context
        options_list, pages = [], []
        if cog.qualified_name == "Gangs":
            filtered = sorted(cog.get_commands(), key=lambda cmd: cmd.name)
        else:
            filtered = await self.filter_commands(cog.walk_commands(), sort=True)

        for chunk in as_chunks(iter(filtered), self.per_page_items):
            options = []
            embed = (
                Embed(color=ctx.author.colour)
                .set_author(
                    name=cog.qualified_name,
                    icon_url=self.get_cog_emoji(cog).url,  # type: ignore
                )
                .set_footer(
                    text=f"Type {ctx.prefix}help <command> for more info",
                    icon_url=ctx.author.display_avatar.url,
                )
            )
            if getattr(cog, "thumbnail", False):
                embed.set_thumbnail(url=cog.thumbnail)  # type: ignore

            for c in chunk:
                if c.parent:
                    continue
                c_usage = c.usage or ""
                embed.add_field(
                    name=f"{ctx.cache.emoji.g_dot} `{ctx.prefix}{c.name} {c_usage}`",
                    value=f"{self.reply} {self.get_command_description(c)}\n⠀",
                    inline=False,
                )
                options.append(
                    SelectOption(
                        label=c.name,
                        value=c.qualified_name,
                        description=c.short_doc or "No Description",
                    )
                )
            pages.append(embed)
            options_list.append(options)
        if not pages:
            raise UserInputError(f"Command or category not found. Use {ctx.prefix}help")
        return pages, SelectCommand(options_list, self)

    def get_cog_list(self) -> tuple[Embed | None, SelectCog]:
        ctx = self.context
        cog_names = ["Miscellaneous"]
        if self.context.channel.id in STAFF_CHANNELS:
            cog_names += ["Developer"]
        cogs = (ctx.bot.get_cog(cog_name) for cog_name in cog_names)
        options = []
        em = (
            Embed(color=ctx.author.colour)
            .set_author(
                name="Help - Getting Started",
                icon_url="https://i.ibb.co/zFNXBRF/Question-mark.png",
            )
            .set_thumbnail(url="https://i.ibb.co/p2kF6XC/help.png")
        )

        for cog in cogs:
            emoji = self.get_cog_emoji(cog)  # type: ignore
            em.add_field(
                name=f"⠀\n{emoji} {cog.qualified_name}",  # type: ignore
                value=f"{self.reply} {cog.description}",
                inline=False,
            )
            options.append(
                SelectOption(
                    emoji=emoji,  # type: ignore
                    label=cog.qualified_name,
                    description=cog.description,
                    value=cog.qualified_name,
                )
            )
        return em, SelectCog(options, self)

    async def send_bot_help(self, _):
        embed, item = self.get_cog_list()
        view = ui.View(timeout=60 * 2)
        view.add_item(item)
        await self.context.reply(embed=embed, view=view)

    async def send_cog_help(self, cog: Cog):
        pages, item = await self.get_cog_help(cog)
        await Paginator(self.context.message, pages, [item]).start()

    async def send_group_help(self, group):
        ctx = self.context
        options_list, pages = [], []
        filtered = filter(
            lambda cmd: not cmd.hidden or cmd.parent,
            sorted(group.commands, key=lambda cmd: cmd.name),
        )
        for chunk in as_chunks(filtered, self.per_page_items):
            options = []
            embed = Embed(
                color=randint(0, 0xFFFFFF),
                title=f"⚙️ {group.qualified_name.capitalize()}",
                description=group.description or None,
            ).set_footer(
                text=f"Type {ctx.prefix}help <command> for more help",
                icon_url=ctx.author.display_avatar.url,
            )
            for c in chunk:
                embed.add_field(
                    name=f"{ctx.cache.emoji.g_dot} `{ctx.prefix}{c.qualified_name} {c.usage or ''}`",
                    value=f"{self.reply} {self.get_command_description(c)}\n⠀",
                    inline=False,
                )
                options.append(
                    SelectOption(
                        label=c.name,
                        value=c.qualified_name,
                        description=c.short_doc or "No Description",
                    )
                )
            pages.append(embed)
            options_list.append(options)
        if not pages:
            raise UserInputError(f"Command or category not found. Use {ctx.prefix}help")
        await Paginator(
            self.context.message, pages, [SelectCommand(options_list, self)]
        ).start()

    async def send_command_help(self, command):
        if command.hidden:
            return
        embed = self.get_command_help(command)
        await self.get_destination().send(
            embed=embed,
            delete_after=None
            if self.context.channel.category_id in COMMAND_CATEGORIES
            else 20,
        )
