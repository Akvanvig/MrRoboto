import sqlalchemy as sa

from sqlalchemy.ext.asyncio import create_async_engine

#
# CLASSES
#

class PostgresDB:
    def __init__(self, config):
        self._wrapped_engine = None

        try:
            db_uri_test = f"postgresql://{config['user']}:{config['password']}@{config['host']}/{config['database']}"

            with sa.create_engine(db_uri_test).connect():
                pass
        except Exception as e:
            self._exists = False
        else:
            self._exists = True
            self._db_uri = f"postgresql+asyncpg://{config['user']}:{config['password']}@{config['host']}/{config['database']}"

        self.meta = sa.MetaData()

    def __getattr__(self, name):
        # Attribute does not exist in PostgresDB,
        # so we check the wrapped engine for a match.
        if not self._wrapped_engine:
            raise AttributeError(name)

        return self._wrapped_engine.__getattribute__(name)

    def exists(self):
        return self._exists

    async def start(self):
        if self._exists and not self._wrapped_engine:
            self._wrapped_engine = create_async_engine(self._db_uri, pool_pre_ping=True)

            async with self._wrapped_engine.begin() as conn:
                    await conn.run_sync(self.meta.create_all)

    async def stop(self):
        if self._wrapped_engine:
            await self._wrapped_engine.dispose()
            self._wrapped_engine = None