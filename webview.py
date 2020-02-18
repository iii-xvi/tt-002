#!/usr/bin/env python3
"""Show results via web-view"""
import shelve

from aiohttp import web

routes = web.RouteTableDef()

stored_data = dict(shelve.open("db.shelve"))


@routes.get('/')
async def index(_request):
    """Just redirect to static file"""
    raise web.HTTPFound("/static/index.html")


@routes.post('/api/search/')
async def api_search(request):
    """Search
    
    :param request: aiohttp request object 
    :return: JSON result
    """
    name_query = (await request.json()).get("q", "").lower()
    # if no name provided, filtration not needed
    if not name_query:
        return web.json_response(stored_data)

    result = {
        "atTime": stored_data['atTime'],
        "events": {},
        "sports": {},
        "sections": {},
    }
    # first filter events
    collected_events_ids = set()
    for event_id, event in stored_data['events'].items():
        if name_query in event['name'].lower():
            result['events'][event_id] = event
            collected_events_ids.add(event_id)

    # fail early
    if not collected_events_ids:
        return web.json_response({})

    # filter relative sections
    required_sports_ids = set()
    for section_id, section in stored_data['sections'].items():
        has_events = [ev_id for ev_id in section['events']
                      if ev_id in collected_events_ids]
        if has_events:
            result['sections'][section_id] = dict(section, events=has_events)
            required_sports_ids.update(result['sports'])

    # filter relative sports
    for sport_id, sport in stored_data['sports'].items():
        if sport_id in required_sports_ids:
            result['sport'][sport_id] = sport

    return web.json_response(result)


routes.static('/static', "./static")

app = web.Application()
app.add_routes(routes)
web.run_app(app)
