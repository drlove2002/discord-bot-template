from __future__ import annotations

from asyncio import create_task

from discord import (
    ButtonStyle,
    Emoji,
    Interaction,
    Member,
    Message,
    PartialEmoji,
    WebhookMessage,
    ui,
)

from mainbot.utils.util import Raise


class SingleLink(ui.View):
    def __init__(
        self,
        url: str,
        label: str = "Jump to message",
        emoji: str | PartialEmoji | Emoji = "🔗",
    ):
        super().__init__()
        self.add_item(ui.Button(label=label, url=url, emoji=emoji))


# noinspection PyUnusedLocal
class YesNo(ui.View):
    children: list[ui.Button]

    def __init__(self, user: Member | None = None):
        super().__init__(timeout=30)
        self.msg: Message | WebhookMessage | None = None
        self.user = user
        self.value = None

    async def interaction_check(self, i: Interaction) -> bool:
        if self.user is None:
            return True
        if i.guild is None or self.user.id == i.user.id:
            return True
        await Raise(i, "You can't use this button").error()
        return False

    async def on_timeout(self) -> None:
        for child in self.children:
            if not child.disabled:
                child.disabled = True
        if self.msg:
            if isinstance(self.msg, WebhookMessage):
                await self.msg.edit(
                    content="You took too long to respond (Interation Closed)",
                    embed=None,
                    view=None,
                )
                return
            await Raise(self.msg, "You took too long to respond", edit=self.msg).error()

    def end_interaction(self, inter: Interaction) -> None:
        self.stop()
        if self.msg:
            create_task(inter.delete_original_response())

    @ui.button(
        style=ButtonStyle.green, emoji="<a:check:1152908387462426774>", label="\u200b"
    )
    async def yes_button(self, button: ui.Button, inter: Interaction):
        self.value = True
        self.end_interaction(inter)

    @ui.button(
        style=ButtonStyle.red, emoji="<a:crossmark:1152907598899728395>", label="\u200b"
    )
    async def cancel_button(self, button: ui.Button, inter: Interaction):
        self.value = False
        self.end_interaction(inter)


ADDED: bool = False
# Change to true after adding persistent_views into the Bot.


def add_persistent_items(bot):
    global ADDED
    if ADDED:
        return
    # bot.add_view(View(bot))
    ADDED = True
