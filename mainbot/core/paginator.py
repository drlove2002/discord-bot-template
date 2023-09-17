from __future__ import annotations

from typing import TYPE_CHECKING

from discord import ButtonStyle, Embed, Interaction, Member, Message, ui

from mainbot.utils.util import Raise

if TYPE_CHECKING:
    from mainbot.cogs.help.views import SelectCommand


__all__ = ["Paginator"]


# noinspection PyArgumentList
class Paginator:
    r"""Paginate the embeds using buttons

    Parameters
    ----------
    message: :class:`Message`
        The message to reply to
    embeds: list[:class:`Embed`]
        The embeds to paginate
    """
    __slots__ = ("msg", "embeds", "view")

    def __init__(
        self,
        message,
        embeds: list[Embed],
        items: list[ui.Item] | None = None,
        auther: Member | None = None,
    ):
        self.msg = message
        self.embeds = embeds
        self.view = PaginatorView(auther or message.author, self.embeds)
        for i in items or []:
            self.view.add_item(i)

    async def start(self, *, edit_msg: Message | None = None):
        if edit_msg:
            if len(self.embeds) < 2:
                self.view._children = self.view.children[4:]
            self.view.msg = await edit_msg.edit(embed=self.embeds[0], view=self.view)
            return
        if len(self.embeds) < 2:
            self.view.msg = await self.msg.reply(embed=self.embeds[0])
        else:
            self.view.msg = await self.msg.reply(embed=self.embeds[0], view=self.view)


class PaginatorView(ui.View):
    r"""The view for the paginator

    Parameters
    ----------
    user: :class:`Member`
        The user to check for
    embeds: list[:class:`Embed`]
        The embeds to paginate
    """

    def __init__(self, user: Member, embeds: list[Embed]):
        super().__init__(timeout=60 * 2)
        self.user = user
        self.embeds = embeds
        self.index = 0
        self.msg: Message | None = None
        self.add_item(
            ui.Button(
                custom_id="page_count",
                label=f"Page {self.index + 1}/{len(self.embeds)}",
                disabled=True,
            )
        )

    async def interaction_check(self, interaction) -> bool:
        if interaction.user == self.user:
            return True
        await Raise(interaction, "You can't use this button").error()
        return False

    async def button_callback(self, inter: Interaction):
        for item in self.children:
            if isinstance(item, ui.Button) and item.custom_id == "page_count":
                item.label = f"Page {self.index + 1}/{len(self.embeds)}"
            if item.custom_id == "command_paginator_dropdown":
                item: SelectCommand
                item.update_options(self.index)

        await inter.response.edit_message(embed=self.embeds[self.index], view=self)

    @ui.button(emoji="⬅️", style=ButtonStyle.gray)
    async def button_left_callback(self, _, inter: Interaction):
        if self.index == 0:
            self.index = len(self.embeds) - 1
        else:
            self.index -= 1

        await self.button_callback(inter)

    @ui.button(emoji="➡️", style=ButtonStyle.gray)
    async def button_right_callback(self, _, inter: Interaction):
        if self.index == len(self.embeds) - 1:
            self.index = 0
        else:
            self.index += 1

        await self.button_callback(inter)

    @ui.button(emoji="🗑", style=ButtonStyle.red)
    async def button_delete_callback(self, _, inter: Interaction):
        self.clear_items()
        await self.button_callback(inter)

    async def on_timeout(self) -> None:
        if len(self.embeds) < 2 or not self.msg:
            return
        await self.msg.edit(embed=self.embeds[self.index], view=None)
