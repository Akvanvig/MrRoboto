import asyncio
import sqlalchemy as sa

from io import StringIO
from aiopg.sa import create_engine
from common.syncfunc import config_h
from psycopg2.errors import DuplicateTable

#
# PUBLIC INTERFACE
#

class Db:
    def __init__(self):
        # Private
        self._engine = None
        self._mock_engine = sa.create_engine('postgres://', strategy="mock", executor=self._mock_dump_sql)
        self._mock_dump = None
        
        # Public
        self.meta = sa.MetaData()
        self.exec_query = self._exec_query_first

    def __del__(self):
        if self._engine: asyncio.run(self._engine.close())

    def _mock_dump_sql(self, sql, *multiparams, **params):
        self._mock_dump = str(sql.compile(dialect=self._mock_engine.dialect))

    # Execute query
    async def _exec_query(self, query):
        async with self._engine.acquire() as conn:
            result = await conn.execute(query)
            return await result.fetchall()

    # Lock subsequent calls and make them wait
    async def _exec_query_wait(self, query):
        while self._engine is None: await asyncio.sleep(1.0)
        self._exec_query(query)

    # Create a new engine before calling _exec_query
    async def _exec_query_first(self, query):
        self.exec_query = self._exec_query_wait
        self._engine = await create_engine(**config_h.get()['postgresql'])

        # We can't call meta.create_all, as we're using
        # a mock_engine to get the sql query, meaning
        # the checkfirst arg is useless. As a result
        # create_all might throw a single DuplicateTable error
        # subsequently dropping to create new non-duplicate ones.
        # Therefore we create each table individually
        # and catch DuplicateTable errors on a per table basis.
        async with self._engine.acquire() as conn:
            for table in self.meta.tables.values():
                try:
                    table.create(bind=self._mock_engine)
                    await conn.execute(self._mock_dump)
                except DuplicateTable:
                    # Table already exist
                    pass

        self.exec_query = self._exec_query
        return await self._exec_query(query)
