import asyncio

# Helpful for when you want to create a timed task
async def run_coro_in(coro, seconds : int):
    await asyncio.sleep(seconds)
    return await coro