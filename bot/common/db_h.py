import asyncio
import sqlalchemy as sa

from aiopg.sa import create_engine
from psycopg2.errors import DuplicateTable

#
# CLASSES
#

class PostgresDB:
    def __init__(self):
        self._wrapped_engine = None
        self._mock_engine = sa.create_engine('postgres://', strategy="mock", executor=self._dump_sql)
        self._mock_dump = None
        self.meta = sa.MetaData()

    def __getattr__(self, name):
        # Attribute does not exist in PostgresDB,
        # so we check the wrapped engine for a match.
        if self._wrapped_engine:
            return self._wrapped_engine.__getattribute__(name)
        else:
            raise AttributeError(name)

    def _dump_sql(self, sql, *multiparams, **params):
        self._mock_dump = str(sql.compile(dialect=self._mock_engine.dialect))

    async def start(self, *args, **kwargs):
        if not self._wrapped_engine:
            self._wrapped_engine = await create_engine(*args, **kwargs)

            # We can't call meta.create_all, as we're using
            # a mock_engine to get the sql query, meaning
            # the checkfirst arg is useless. As a result
            # create_all might throw a single DuplicateTable error
            # subsequently dropping to create new non-duplicate ones.
            # Therefore we create each table individually
            # and catch DuplicateTable errors on a per table basis.
            async with self._wrapped_engine.acquire() as conn:
                for table in self.meta.tables.values():
                    try:
                        table.create(bind=self._mock_engine)
                        await conn.execute(self._mock_dump)
                    except DuplicateTable:
                        # Table already exist
                        pass

    async def stop(self):
        if self._wrapped_engine: 
            self._wrapped_engine.close()
            await self._wrapped_engine.wait_closed()
            self._wrapped_engine = None