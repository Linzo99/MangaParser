from src.MangakakalotParser import _MangakakalotParser
from src.ManganeloParser import _ManganeloParser
from src.MangaseeParser import _MangaseeParser
import asyncio

class MangaParser:
        loop = asyncio.get_event_loop()

        def __init__(self):
                self.parsers = [_MangakakalotParser(), _ManganeloParser()]

        async def _query(self, name, epis=None):
                found = await asyncio.gather(self.parsers[0].get(name, epis),
                                       self.parsers[1].get(name, epis),
                                       #self.parsers[2].get(name, epis)
                                       )
                return found

        def get(self, name, epis=None):
                result = self.loop.run_until_complete(self._query(name, epis))
                return result

        async def async_get(self, name, epis=None):
                result = await self._query(name, epis)
                return result

