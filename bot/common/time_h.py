"""
Time regular expression taken from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
"""

import re
import inspect
import asyncio

from .db_h import PostgresDB
from functools import partial
from datetime import timezone, datetime, timedelta
from discord.utils import sleep_until
from discord.backoff import ExponentialBackoff

# Errors
from discord import HTTPException, GatewayNotFound, ConnectionClosed
from discord.ext.commands import ArgumentParsingError
from aiohttp import ClientError
from websockets import InvalidHandshake, WebSocketProtocolError

#
# PRIVATE INTERFACE
#

_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
_UNITS = {
    's':'seconds',
    'm':'minutes',
    'h':'hours',
    'd':'days',
    'w':'weeks'
}
_TIMEREG = re.compile(r"(?P<val>\d+)(?P<unit>[smhdw]?)", flags=re.I)

_VALID_EXCEPTIONS = (
    OSError,
    HTTPException,
    GatewayNotFound,
    ConnectionClosed,
    ClientError,
    asyncio.TimeoutError,
    InvalidHandshake,
    WebSocketProtocolError,
)


#
#  PUBLIC INTERFACE
#

DEFAULT_TIMEDELTA = timedelta()

class datetime_ext(datetime):
    def __str__(self):
        return self.strftime(_DATEFORMAT)

    @classmethod
    def from_str(cls, s : str):
        return cls.strptime(s, _DATEFORMAT).replace(tzinfo=timezone.utc)

    @classmethod
    async def convert(cls, ctx, argument):
        try:
            return cls.from_str(argument)
        except ValueError:
            raise ArgumentParsingError(f'Could not parse "{argument}" to a valid date.')

    @classmethod
    def now(cls):
        return super(datetime_ext, cls).now(timezone.utc)

class timedelta_ext(timedelta):
    @classmethod
    async def convert(cls, ctx, argument):
        parsed_time = {_UNITS.get(m.group('unit').lower(), 'seconds'): int(m.group('val')) for m in _TIMEREG.finditer(argument)}

        if not parsed_time:
            raise ArgumentParsingError(f'Could not parse "{argument}" to a valid time.')

        return cls(**parsed_time)

    def to_datetime_now(self):
        return datetime_ext.now() + self

# TODO(Fredrico): Improve duplication?
class Task:
    def __init__(self, loop, on_start, on_end , timedelta, *, reconnect = True):
        if on_start and not (inspect.iscoroutinefunction(on_start) or isinstance(on_start, partial)):
            raise TypeError('Expected coro function or partial object, received {0.__name__!r}.'.format(type(on_start)))

        # There must be an on_end
        if not (inspect.iscoroutinefunction(on_end) or isinstance(on_end, partial)):
            raise TypeError('Expected coro function or partial object, received {0.__name__!r}.'.format(type(on_end)))

        if not isinstance(timedelta, timedelta_ext):
            raise TypeError('Expected timedelta_ext object, received {0.__name__!r}.'.format(type(timedelta)))

        self.on_start = on_start
        self.on_end = on_end
        self.timedelta = timedelta
        self._loop = loop or asyncio.get_event_loop()
        self._task = None
        self.failed_exc = None
        self._reconnect = reconnect

    async def _start(self):
        self.failed_exc = None

        try:
            if self.on_start:
                await self.on_start()

            await sleep_until(self.timedelta.to_datetime_now())

            while True:
                try:
                    await self.on_end()
                    return
                except _VALID_EXCEPTIONS as exc:
                    if not self._reconnect:
                        raise
                    await asyncio.sleep(ExponentialBackoff().delay())
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.failed_exc = exc
            raise exc

    def cancelled(self):
        if self._task:
            return self._task.cancelled()
        return None

    def failed(self):
        if not self.failed_exc is None:
            return True
        return False

    def start(self):
        if self._task is not None and not self._task.done():
            raise RuntimeError("Task is already launched and is not completed.")

        self._task = self._loop.create_task(self._start())

        return self._task

    def stop(self):
        if self._task and not self._task.done():
            self._task.cancel()

    async def wait(self):
        if self._task:
            try:
                await self._task
            except asyncio.CancelledError:
                pass
