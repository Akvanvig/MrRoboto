"""
Time regular expression taken from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
"""

import re
import inspect
import asyncio

from .db import PostgresDB
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
_REGCOMPILED = re.compile(r"(?P<val>\d+)(?P<unit>[smhdw]?)", flags=re.I)

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

# TODO(Fredrico): Use native __str__ conversion instead of to_str
class datetime_ext(datetime):
    @classmethod
    async def convert(cls, ctx, argument):
        try:
            return cls.from_str(argument)
        except ValueError:
            raise ArgumentParsingError('Could not parse "{}" to a valid date.'.format(argument))

    @classmethod
    def now(cls):
        return super(datetime_ext, cls).now(timezone.utc)

    @classmethod
    def from_str(cls, s : str):
        return cls.strptime(s, _DATEFORMAT).replace(tzinfo=timezone.utc)

    def to_str(self):
        return self.strftime(_DATEFORMAT)

class timedelta_ext(timedelta):
    @classmethod
    async def convert(cls, ctx, argument):
        parsed_time = {_UNITS.get(m.group('unit').lower(), 'seconds'): int(m.group('val')) for m in _REGCOMPILED.finditer(argument)}

        if not parsed_time:
            raise ArgumentParsingError('Could not parse "{}" to a valid time.'.format(argument))

        return cls(**parsed_time)

    def to_datetime_now(self):
        return datetime_ext.now() + self

class Task:
    def __init__(self, client, coro, timedelta, start_stmt = None, end_stmt = None, *, reconnect = True, start = True):
        if not (inspect.iscoroutinefunction(coro) or isinstance(coro, partial)):
            raise TypeError('Expected coro function or partial object, received {0.__name__!r}.'.format(type(coro)))

        if not isinstance(timedelta, timedelta_ext):
            raise TypeError('Expected timedelta_ext object, received {0.__name__!r}.'.format(type(timedelta)))

        self.coro = coro
        self.timedelta = timedelta
        self.start_stmt = start_stmt
        self.end_stmt = end_stmt
        self.failed_exc = False
        self._client = client
        self._reconnect = reconnect
        self._task = self._client.loop.create_task(self._start()) if start else None

    def cancelled(self):
        if self._task:
            return self._task.cancelled()

    def failed(self):
        if not self.failed_exc is None:
            return True
        return False
        
    def start(self):
        if self._task is not None and not self._task.done():            
            raise RuntimeError('Task is already launched and is not completed.')

        self._task = asyncio.create_task(self._start())
        
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

    async def _start(self):
        self.failed_exc = None

        try:
            await self._run_stmt(self.start_stmt)
            
            await sleep_until(self.timedelta.to_datetime_now())
            try:
                await self.coro()
            except _VALID_EXCEPTIONS as exc:
                if not self._reconnect:
                    raise
                await asyncio.sleep(ExponentialBackoff().delay())
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            self.failed_exc = exc
            raise exc
        finally:
            await self._run_stmt(self.end_stmt)

    async def _run_stmt(self, stmt):
        if not stmt is None:
            async with self._client.db.acquire() as conn:
                await conn.execute(stmt)