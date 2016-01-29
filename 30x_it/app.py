import os
import string
import random
import asyncio
from pathlib import Path

from . import config

import jinja2
import aioredis
import aiohttp_jinja2
from aiohttp import web


def _generate_token():
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))


async def redirect(request):
    path = request.path_qs
    host = request.headers.get('host')
    r = await aioredis.create_redis((config.host, config.port))
    config = await r.hgetall('host:' + host)
    if not config:
        raise web.HTTPBadRequest
    raise web.HTTPMovedPermanently(config['target'])


@aiohttp_jinja2.template('index.html.j2')
async def index(request):
    return {}


async def update_rule(request):
    config = await request.post()
    token = request.match_info.get('token')
    host = config['host']
    code = config.get('code', '301')
    target = config['target']
    keep_path = config.get('keep_path', '0')
    r = await aioredis.create_redis((config.host, config.port))
    if not await r.sismember('tokens:' + token, host):
        raise web.HTTPForbidden
    await r.hmset('hosts:' + host,
        'target', target,
        'code', code,
        'keep_path', keep_path,
    )
    raise web.HTTPFound(app.router['get_rules'].url(parts={'token': token}))


async def add_rule(request):
    config = await request.post()
    host = config['host']
    code = config.get('code', '301')
    target = config['target']
    keep_path = config.get('keep_path', '0')
    r = await aioredis.create_redis((config.host, config.port))
    if await r.exists('hosts:' + host):
        raise web.HTTPForbidden
    token = config.get('token', _generate_token())
    pipeline = r.multi_exec()
    pipeline.sadd('tokens:' + token, host)
    pipeline.hmset('hosts:' + host,
        'target', target,
        'code', code,
        'keep_path', keep_path,
        'token', token,
    )
    await pipeline.execute()
    raise web.HTTPFound(app.router['get_rules'].url(parts={'token': token}))


@aiohttp_jinja2.template('rules.html.j2')
async def get_rules(request):
    token = request.match_info.get('token')
    r = await aioredis.create_redis((config.host, config.port))
    hosts = [x.decode() for x in await r.smembers('tokens:' + token)]
    pipeline = r.multi_exec()
    for host in hosts:
        pipeline.hgetall('hosts:' + host)
    rules = [
        {k.decode(): v.decode() for k, v in d.items()}
        for d in await pipeline.execute()
    ]

    for host, rule in zip(hosts, rules):
        rule['host'] = host

    return {'token': token, 'rules': rules}


app = web.Application()
app.router.add_route('GET', '/', index, name='index')
app.router.add_route('POST', '/rules', add_rule, name='add_rule')
app.router.add_route('GET', '/rules/{token}', get_rules, name='get_rules')
app.router.add_route('POST', '/rules/{token}', update_rule, name='update_rule')
app.router.add_route('*', '/{path}', redirect, name='redirect')

aiohttp_jinja2.setup(
    app, loader=jinja2.FileSystemLoader(str(Path(__file__).parent / 'templates'))
)

if __name__ == '__main__':
    async def init(loop, app):
        srv = await loop.create_server(app.make_handler(), '0.0.0.0', 8080)
        return srv

    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop, app))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
