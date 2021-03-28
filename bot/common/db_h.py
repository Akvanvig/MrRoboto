import asyncio
import sqlalchemy as sa

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
            self._wrapped_engine = sa.ext.asyncio.create_async_engine(
                f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
            )

            async with self._wrapped_engine.begin() as conn:
                await conn.run_sync(self.meta.create_all)

    async def stop(self):
        if self._wrapped_engine: 
            await self._wrapped_engine.dispose()
            self._wrapped_engine = None