import asyncio

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine

from aiopg.sa import create_engine
from psycopg2.errors import DuplicateTable

#
# CLASSES
#

class PostgresDB:
    def __init__(self):
        self._wrapped_engine = None
        self.meta = sa.MetaData()

    def __getattr__(self, name):
        # Attribute does not exist in PostgresDB,
        # so we check the wrapped engine for a match.
        if self._wrapped_engine:
            return self._wrapped_engine.__getattribute__(name)
        else:
            raise AttributeError(name)

    async def start(self, config):
        if not self._wrapped_engine:
            self._wrapped_engine = create_async_engine(
                f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
            )

            async with engine.begin() as conn:
                await conn.run_sync(self.meta.create_all)

    async def stop(self):
        if self._wrapped_engine: 
            await _wrapped_engine.dispose()
            self._wrapped_engine = None