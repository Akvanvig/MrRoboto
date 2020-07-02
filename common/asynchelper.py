import asyncio

async def run_coro_in(coro, seconds : int):
    await asyncio.sleep(seconds)
    return await coro