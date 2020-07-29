import asyncio
import sqlalchemy as sa

from io import StringIO
from aiopg.sa import create_engine
from common.syncfunc import config_h
from psycopg2.errors import DuplicateTable

#
# PRIVATE INTERFACE
#

class Db():
    def __init__(self):
        self._engine = None
        self._mock_engine = sa.create_engine('postgres://', strategy="mock", executor=self._mock_dump_sql)
        self._mock_dump = None

    # Cleanup engine
    def __del__(self):
        if self._engine is None: return
        
        asyncio.run(self._engine.close())
        self._engine = None

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
        global exec_query

        exec_query = self._exec_query_wait
        self._engine = await create_engine(**config_h.get()['postgresql'])

        # Create tables if possible
        async with self._engine.acquire() as conn:
            try:
                META.create_all(bind=self._mock_engine)
                await conn.execute(self._mock_dump)
            except DuplicateTable:
                # Tables already exist
                pass

        exec_query = self._exec_query
        return await self._exec_query(query)


_DB = Db()

#
# PUBLIC INTERFACE
#

META = sa.MetaData()
exec_query = _DB._exec_query_first