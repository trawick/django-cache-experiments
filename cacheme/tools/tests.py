from django.test import TestCase

import data

# Create your tests here.


class BasicTests(TestCase):

    def setUp(self):
        self.object = data.build()
        self.key = 'Jeff'

    def test_basic_operation(self):
        for rs in data.REDIS_SERIALIZERS:
            data.redis_store(self.key, self.object, serializer=rs)
            tmp_data = data.redis_retrieve(self.key, serializer=rs)
            assert tmp_data
            assert tmp_data == self.object, 'mismatch with redis store with serializer %s' % str(rs)

        for cn in data.DJANGO_CACHE_NAMES:
            data.djcache_store(self.key, self.object, cache_name=cn)
            tmp_data = data.djcache_retrieve(self.key, cache_name=cn)
            assert tmp_data, 'couldn\'t load object from Django %s cache' % cn
            assert tmp_data == self.object, 'mismatch with Django store with cache %s (%s vs. %s)' % \
                                            (cn, str(self.object)[:100], str(tmp_data)[:100])
