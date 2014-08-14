import os
import sys
import timeit

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'cacheme.settings')
sys.path.append('.')

import data

global_test_data = None
global_api_name = None


def cache_set(name):
    fns = data.APIS[name]
    fns[0]('mykey', global_test_data)


def time_cache_lookup(name):
    fns = data.APIS[name]
    got_back = fns[1]('mykey')
    assert got_back == global_test_data


def lookup_timings(count):
    global global_api_name, global_test_data

    global_test_data = data.build(num_outer=1000, num_inner=1000)
    for global_api_name in data.APIS:
        # Why skip these?
        #  MemcachedCache: may need extra config to support large objects
        #  DatabaseCache: too slow
        #  LocMemCache: need something shared between processes
        if global_api_name in ['MemcachedCache', 'DatabaseCache']:
            continue
        if global_api_name is not None:
            printable = global_api_name
        else:
            printable = 'None'
        cache_set(global_api_name)
        print '%-20s:' % printable, timeit.timeit('time_cache_lookup(global_api_name)', number=count,
                                                  setup="from __main__ import time_cache_lookup, global_api_name")


def process(args):
    try:
        count = int(args[1])
    except IndexError:
        print >> sys.stderr, 'Please tell me how many iterations'
        sys.exit(1)
    except ValueError:
        print >> sys.stderr, 'Please check the number of iterations'
        sys.exit(1)
    lookup_timings(count)

if __name__ == '__main__':
    process(sys.argv)
