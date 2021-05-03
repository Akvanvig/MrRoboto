import sqlalchemy as sa

from sqlalchemy.ext.asyncio import create_async_engine

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
        if not self._wrapped_engine:
            raise AttributeError(name)

        return self._wrapped_engine.__getattribute__(name)

    def connected(self):
        return True if self._wrapped_engine else False

    async def start(self, config):
        if not self._wrapped_engine:
            engine = create_async_engine(
                f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['database']}"
            )

            try:
                async with engine.begin() as conn:
                    await conn.run_sync(self.meta.create_all)
            except Exception as e:
                print(e)
            else:
                self._wrapped_engine = engine

    async def stop(self):
        if self._wrapped_engine:
            await self._wrapped_engine.dispose()
            self._wrapped_engine = None