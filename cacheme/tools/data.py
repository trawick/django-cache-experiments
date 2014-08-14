import functools
import json
import pickle
import logging

from django.conf import settings
from django.core.cache import get_cache
import redis

logger = logging.getLogger(__name__)

report_store = redis.StrictRedis()

REDIS_SERIALIZERS = ['json', 'pickle', None]
DJANGO_CACHE_NAMES = [k for k in settings.CACHES.keys() if k != 'default']


def redis_retrieve(key, serializer=None):
    if serializer:
        if serializer == 'json':
            key = 'json-' + key
        elif serializer == 'pickle':
            key = 'pickle-' + key
    data_out = report_store.get(key)
    if data_out is not None:
        logger.debug('returning %s from cache' % key)
        if serializer:
            if serializer == 'json':
                data_out = json.loads(data_out)
            elif serializer == 'pickle':
                data_out = pickle.loads(data_out)
        else:
            data_out = eval(data_out)
    else:
        logger.error('%s not available in the cache and won\'t be generated' % key)
    return data_out


def redis_store(key, data, serializer=None):
    if serializer:
        if serializer == 'json':
            key = 'json-' + key
            data = json.dumps(data)
        elif serializer == 'pickle':
            key = 'pickle-' + key
            data = pickle.dumps(data)
    report_store.set(key, data)


def djcache_retrieve(key, cache_name=None):
    cache = get_cache(cache_name)
    assert cache
    data_out = cache.get(key)
    if data_out is not None:
        logger.debug('returning %s from cache' % key)
    else:
        logger.error('%s not available in the cache and won\'t be generated' % key)
    return data_out


def djcache_store(key, data, cache_name=None):
    cache = get_cache(cache_name)
    assert cache
    cache.set(key, data)


def build(num_outer=100, num_inner=100):
    """ Note: memcached backend will fail if size > 1MB, depending on memcached setup
    """
    d = dict()
    for i in range(num_outer):
        key = 'key %0000d' % i
        d[key] = []
        for j in range(num_inner):
            d[key].append('January %d' % j)
    return d


def django_cache_apis(cache_name):
    return (functools.partial(djcache_store, cache_name=cache_name),
            functools.partial(djcache_retrieve, cache_name=cache_name))


def redis_cache_apis(serializer):
    return (functools.partial(redis_store, serializer=serializer),
            functools.partial(redis_retrieve, serializer=serializer))

DJCACHE_APIS = {cache_name: django_cache_apis(cache_name) for cache_name in DJANGO_CACHE_NAMES}
REDIS_APIS = {serializer: redis_cache_apis(serializer) for serializer in REDIS_SERIALIZERS}

APIS = dict(DJCACHE_APIS.items() + REDIS_APIS.items())
