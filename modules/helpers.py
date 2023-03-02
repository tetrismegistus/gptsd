import asyncio

class AsyncSafeList:
    def __init__(self):
        self._list = []
        self._lock = asyncio.Lock()
        self._index = 0

    def __aiter__(self):
        self._index = 0
        return self

    async def __anext__(self):
        async with self._lock:
            if self._index < len(self._list):
                item = self._list[self._index]
                self._index += 1
                return item
            else:
                raise StopAsyncIteration

    async def append(self, item):
        async with self._lock:
            self._list.append(item)
            if len(self._list) > 6:
                self._list.pop(0)

    async def remove(self, item):
        async with self._lock:
            self._list.remove(item)

    async def get(self, index):
        async with self._lock:
            return self._list[index]

    async def __len__(self):
        async with self._lock:
            return len(self._list)

