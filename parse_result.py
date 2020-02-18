#!/usr/bin/env python3
import asyncio
import shelve
import time
from random import choice
from time import time

import aiohttp


async def get_results(srv_idx:int=None, locale:str='ru') -> dict:
    """Get results via API call

    :param srv_idx: Clients API server index
    :param locale: Result locale
    :returns: Results data

    there async not really needed but i don't want additional requirements
    which can make this simpler (e.g. requests)
    """
    _now_stamp = time()

    if srv_idx is None:
        srv_idx = choice([11, ])  # manually described ids

    url = f"https://clientsapi{srv_idx}.bkfon-resource.ru/results/" \
          f"results.json.php?locale={locale}&lastUpdate=0&_={_now_stamp}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


async def main():
    res = await get_results()

    def _list_to_map(items):
        return {int(item.pop('id')): item for item in items}

    result = {
        "sections": _list_to_map(res['sections']),
        "sports": _list_to_map(res['sports']),
        "events": _list_to_map(res['events']),
        'atTime': res['lineDate']
    }

    db = shelve.open("db.shelve")
    db.update(result)

    pass


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
