import os

from redis.client import Pipeline as Pipe
from redis.client import StrictRedis

from mainbot.utils.logging import get_logger

logger = get_logger(__name__)


class RedisClient(StrictRedis):
    """Implementation of KeyDB client.

    KeyDB is a high performance open source database used at Snap,
    and a powerful drop-in alternative to Redis."""

    def __init__(self, host=os.getenv("DB_HOST", "localhost")):
        super().__init__(
            password=os.environ["REDIS_PASS"],
            host=host,
            decode_responses=True,
        )
        for cmd, callback in {"SADDEX": int}.items():
            self.set_response_callback(cmd, callback)

    def saddex(self, key: str, delay: int, *subkey: str) -> bool:
        """
        Simimar to SADD but adds one or more members that expire after
        specified number of seconds. An error is returned when the value
        stored at `key` is not a set.

        For more information see https://www.dragonflydb.io/docs/command-reference/sets/saddex
        """
        args = ["SADDEX", key, delay, *subkey]
        return self.execute_command(*args)

    def lrotate(self, key: str) -> str:
        """Put first item of the list to the laft and return it."""
        return self.lmove(key, key)


class Pipeline(RedisClient, Pipe):
    """A Request/Response server can be implemented so that it is able to process new
    requests even if the client hasn't already read the old responses.
    This way it is possible to send multiple commands to the server without
    waiting for the replies at all, and finally read the replies in a single step."""
