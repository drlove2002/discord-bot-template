import sys
from os import environ

from mainbot.core.bot import BaseMainBot
from mainbot.utils import logging

bot = BaseMainBot()
logger = logging.get_logger(__name__)


def main():
    bot.run(
        environ["TOKEN"],
        log_handler=logging.ch,
        log_formatter=logging.ch.formatter,
        log_level=logging.ch.level,
    )


if __name__ == "__main__":
    try:
        if sys.platform not in ("win32", "cygwin", "cli"):
            import uvloop

            uvloop.install()
    except ImportError:
        logger.info("UVLoop can't be installed in windows")
    main()
