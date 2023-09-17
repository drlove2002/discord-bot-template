from __future__ import annotations

from typing import TYPE_CHECKING

from discord import Interaction, SelectOption, ui
from discord.ext.commands import UserInputError

from mainbot.core.paginator import Paginator

if TYPE_CHECKING:
    from .embed_utilizer import EmbedHelpCommand


class SelectCommand(ui.Select):
    def __init__(
        self, mapping: list[list[SelectOption]], help_command: EmbedHelpCommand
    ):
        self.help = help_command
        self.index = 0
        self.options_list = mapping
        super().__init__(
            placeholder="⚙️More about commands",
            options=self.options_list[self.index],
            custom_id="command_paginator_dropdown",
        )

    def update_options(self, index):
        self.index = index
        self.options = self.options_list[self.index]

    async def callback(self, inter: Interaction):
        embed = self.help.get_command_help(
            self.help.context.bot.get_command(self.values[0])
        )
        await inter.response.send_message(embed=embed, ephemeral=True)


class SelectCog(ui.Select):
    def __init__(self, options: list[SelectOption], help_command: EmbedHelpCommand):
        self.help = help_command
        self.bot = help_command.context.bot
        super().__init__(
            placeholder="⚙️Select a category",
            options=options,
            custom_id="cog_paginator_dropdown",
        )

    async def callback(self, inter: Interaction):
        try:
            embeds, item = await self.help.get_cog_help(
                self.bot.get_cog(self.values[0])
            )
        except UserInputError:
            return await inter.response.send_message(
                "Something went wrong, please try again later", ephemeral=True
            )
        await Paginator(self.help.context.message, embeds, [self, item]).start(
            edit_msg=inter.message
        )
