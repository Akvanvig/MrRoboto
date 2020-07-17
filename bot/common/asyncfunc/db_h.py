import asyncio
import sqlalchemy as sa

from io import StringIO
from aiopg.sa import create_engine
from common.syncfunc import config_h

#
# PRIVATE INTERFACE
#

# TODO(Fredrico): Cleanup private interface

_engine = None
_meta = sa.MetaData()

# Workaround for aiopg not allowing create_all directly
def _dump_sql(func, *args, **kwargs):
    out = StringIO()

    def dump(sql, *multiparams, **params):
        out.write(str(sql.compile(dialect=dump.dialect)))

    engine = sa.create_engine('postgres://', strategy="mock", executor=dump)
    dump.dialect = engine.dialect

    func(*args, bind=engine, **kwargs)

    return out.getvalue()

async def _getEngine():
    global _engine

    if _engine is None:
        _engine = await create_engine(**config_h.get()['postgresql'])
        
        # Create tables if possible
        async with _engine.acquire() as conn:
            await conn.execute(_dump_sql(_meta.create_all))

    return _engine

#
# PUBLIC INTERFACE
#

MUTED_TABLE = sa.Table(
    'muted', _meta,
    sa.Column('guild_id', sa.Integer, primary_key = True),
    sa.Column('user_id', sa.Integer, primary_key = True),
    sa.Column('unmutedate', sa.String, nullable = False)
)

async def exec_query(query):
    engine = await _getEngine()
    async with engine.aquire() as conn:
        return await conn.execute(query)