from __future__ import annotations

from typing import TYPE_CHECKING
from urllib.request import urlopen

from discord import CategoryChannel
from discord import Role as DiscordRole
from discord import TextChannel
from discord.utils import find

if TYPE_CHECKING:
    from mainbot.core.bot import MainBot

NORMALIZE_CHARS = {
    "Š": "S",
    "š": "s",
    "Ð": "Dj",
    "Ž": "Z",
    "ž": "z",
    "À": "A",
    "Á": "A",
    "Ã": "A",
    "Ä": "A",
    "Å": "A",
    "Æ": "A",
    "Ç": "C",
    "È": "E",
    "É": "E",
    "Ê": "E",
    "Ë": "E",
    "Ì": "I",
    "Í": "I",
    "Ï": "I",
    "Ñ": "N",
    "Ń": "N",
    "Ò": "O",
    "Ó": "O",
    "Ô": "O",
    "Õ": "O",
    "Ö": "O",
    "Ø": "O",
    "Ù": "U",
    "Ú": "U",
    "Û": "U",
    "Ü": "U",
    "Ý": "Y",
    "Þ": "B",
    "ß": "Ss",
    "à": "a",
    "á": "a",
    "ã": "a",
    "ä": "a",
    "å": "a",
    "æ": "a",
    "ç": "c",
    "è": "e",
    "é": "e",
    "ê": "e",
    "ë": "e",
    "ì": "i",
    "í": "i",
    "ï": "i",
    "ð": "o",
    "ñ": "n",
    "ń": "n",
    "ò": "o",
    "ó": "o",
    "ô": "o",
    "õ": "o",
    "ö": "o",
    "ø": "o",
    "ù": "u",
    "ú": "u",
    "û": "u",
    "ü": "u",
    "ý": "y",
    "þ": "b",
    "ÿ": "y",
    "ƒ": "f",
    "ă": "a",
    "î": "i",
    "â": "a",
    "ș": "s",
    "ț": "t",
    "Ă": "A",
    "Î": "I",
    "Â": "A",
    "Ș": "S",
    "Ț": "T",
}
ALPHABETS = (
    urlopen(
        "https://raw.githubusercontent.com/JEF1056/clean-discord/master/src/alphabets.txt"
    )
    .read()
    .decode("utf-8")
    .strip()
    .split("\n")
)
for alphabet in ALPHABETS[1:]:
    alphabet = alphabet
    for ind, char in enumerate(alphabet):
        try:
            NORMALIZE_CHARS[char] = ALPHABETS[0][ind]
        except KeyError:
            print(alphabet, len(alphabet), len(ALPHABETS[0]))
            break
NORMALIZE_CHARS = dict(NORMALIZE_CHARS)


class Role:
    def __init__(self, bot: MainBot):
        self._bot = bot
        self.admin = self.from_name("Admin")  # TODO: Change with real names
        self.staff = self.from_name("Staff")

    def from_name(self, name: str) -> DiscordRole | None:
        return find(lambda r: r.name.lower() == name.lower(), self._bot.guild().roles)


class Emoji:
    def __init__(self, bot: MainBot):
        self.alert = bot.get_emoji(1152907495191351316)
        self.cross = bot.get_emoji(1152907598899728395)
        self.check = bot.get_emoji(1152908387462426774)
        self.g_dot = bot.get_emoji(1152907365994217503)
        self.loading = bot.get_emoji(1152863463476047874)


class Channel:
    """Some import channel of servers"""

    def __init__(self, bot: MainBot):
        self._bot = bot
        # TODO: Edit channel names as per your server
        self.dev_chat: TextChannel = self.from_name("♕│dev-chat")
        self.log: TextChannel = self.from_name("📂│islam-logs")
        self.command: TextChannel = self.from_name("🤖│bot")

    def from_name(self, name: str) -> TextChannel | None:
        return find(
            lambda r: r.name.lower() == name.lower(), self._bot.guild().text_channels
        )


class Category:
    """Some import category of servers"""

    def __init__(self, bot: MainBot):
        self._bot = bot
        # TODO: Edit category names as per your server
        self.staff: CategoryChannel = self.from_name("💭 | Staff Main")

    def from_name(self, name: str) -> CategoryChannel | None:
        return find(
            lambda r: r.name.lower() == name.lower(), self._bot.guild().categories
        )
