import asyncio

class FilterQueue(asyncio.Queue):
    lock = asyncio.Lock()

    @property
    def window(self):
        return self._queue[0] if self._queue else None

    def init(self, *args, **kwargs):
        super().init(*args, **kwargs)

    async def later(self):
        async with self.lock:
            if self.empty():
                raise asyncio.QueueEmpty
            else:
                item = self._get()
                self._put(item)

    def filter_in(self, filter):
        for item in self._queue:
            if filter(item):
                return True
        return False

    async def put(self, item):
        await super().put(item)

    async def get(self, filter=None):
        if filter is not None:
            if self.filter_in(filter):
                while not filter(self.window):
                    await self.later()
            return await super().get()
        else:
            return await super().get()

async def putter(n, queue):
    for i in range(n):
        await queue.put(i)

async def getter(n, queue, filter):
    for i in range(n):
        await asyncio.sleep(0.1)
        yield await queue.get(filter)

async def main():
    queue = FilterQueue(10)
    asyncio.create_task(putter(20, queue))
    async for res in getter(20, queue, lambda n: n % 2):
        print(res)

asyncio.run(main())
