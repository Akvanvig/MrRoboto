"""
Time regular expression taken from https://stackoverflow.com/questions/3096860/convert-time-string-expressed-as-numbermhdsw-to-seconds-in-python
"""

import re
import inspect
import discord
import aiohttp
import asyncio
import websockets

from functools import partial
from datetime import timezone, datetime, timedelta
from discord.utils import sleep_until
from discord.backoff import ExponentialBackoff
from discord.ext.tasks import Loop
from discord.ext.commands import ArgumentParsingError

#
# PRIVATE INTERFACE
#

_DATEFORMAT = '%Y-%m-%d %H:%M:%S'
_UNITS = {'s':'seconds', 
         'm':'minutes', 
         'h':'hours', 
         'd':'days', 
         'w':'weeks'}
_REGCOMPILED = re.compile(r"(?P<val>\d+)(?P<unit>[smhdw]?)", flags=re.I)

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

# TODO(Fredrico): 
# * Add decorator to make it feature complete versus discord.ext.tasks Loop
# * Update __doc__ strings
class Task(Loop):
    def __init__(self, coro, seconds = 0, hours = 0, minutes = 0, count = 1, delay = False, reconnect = True, loop = None):
        self.coro = coro
        self.reconnect = reconnect
        self.loop = loop or asyncio.get_event_loop()
        self.count = count
        self._delay_loop = delay
        self._current_loop = 0
        self._task = None
        self._injected = None
        self._valid_exception = (
            OSError,
            discord.HTTPException,
            discord.GatewayNotFound,
            discord.ConnectionClosed,
            aiohttp.ClientError,
            asyncio.TimeoutError,
            websockets.InvalidHandshake,
            websockets.WebSocketProtocolError,
        )

        self._before_loop = None
        self._after_loop = None
        self._is_being_cancelled = False
        self._has_failed = False
        self._stop_next_iteration = False

        if self.count is not None and self.count <= 0:
            raise ValueError('count must be greater than 0 or None.')

        self.change_interval(seconds=seconds, minutes=minutes, hours=hours)
        self._last_iteration = None
        self._next_iteration = None

        if not (inspect.iscoroutinefunction(self.coro) or isinstance(self.coro, partial)):
            raise TypeError('Expected coro function or partial object, not {0.__name__!r}.'.format(type(self.coro)))

    async def _loop(self, *args, **kwargs):
        backoff = ExponentialBackoff()
        await self._call_loop_function('before_loop')

        if self._delay_loop:
            await sleep_until(datetime.now(timezone.utc) + timedelta(seconds=self._sleep))

        self._next_iteration = datetime.now(timezone.utc)

        try:
            # allows cancelling in before_loop
            await asyncio.sleep(0)
    
            while True:
                self._last_iteration = self._next_iteration
                self._next_iteration = self._get_next_sleep_time()
                try:
                    await self.coro(*args, **kwargs)
                    now = datetime.now(timezone.utc)
                    if now > self._next_iteration:
                        self._next_iteration = now
                except self._valid_exception as exc:
                    if not self.reconnect:
                        raise
                    await asyncio.sleep(backoff.delay())
                else:
                    if self._stop_next_iteration:
                        return
                    self._current_loop += 1
                    if self._current_loop >= self.count:
                        break

                    await sleep_until(self._next_iteration)
        except asyncio.CancelledError:
            self._is_being_cancelled = True
            raise
        except Exception as exc:
            self._has_failed = True
            await self._call_loop_function('error', exc)
            raise exc
        finally:
            await self._call_loop_function('after_loop')
            self._is_being_cancelled = False
            self._current_loop = 0
            self._stop_next_iteration = False
            self._has_failed = False

    def before_loop(self, coro):
        """A decorator that registers a coroutine to be called before the loop starts running.
        This is useful if you want to wait for some bot state before the loop starts,
        such as :meth:`discord.Client.wait_until_ready`.
        The coroutine must take no arguments (except ``self`` in a class context).
        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register before the loop runs.
        Raises
        -------
        TypeError
            The function was not a coroutine.
        """

        if not (inspect.iscoroutinefunction(coro) or isinstance(coro, partial)):
            raise TypeError('Expected coro function or partial object, received {0.__name__!r}.'.format(type(coro)))

        self._before_loop = coro
        return coro

    def after_loop(self, coro):
        """A decorator that register a coroutine to be called after the loop finished running.
        The coroutine must take no arguments (except ``self`` in a class context).
        .. note::
            This coroutine is called even during cancellation. If it is desirable
            to tell apart whether something was cancelled or not, check to see
            whether :meth:`is_being_cancelled` is ``True`` or not.
        Parameters
        ------------
        coro: :ref:`coroutine <coroutine>`
            The coroutine to register after the loop finishes.
        Raises
        -------
        TypeError
            The function was not a coroutine.
        """

        if not (inspect.iscoroutinefunction(coro) or isinstance(coro, partial)):
            raise TypeError('Expected coro function or partial object, received {0.__name__!r}.'.format(type(coro)))

        self._after_loop = coro
        return coro