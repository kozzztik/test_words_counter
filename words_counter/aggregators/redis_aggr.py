from base import BaseAggregator, BaseWorkerAggregator
from redis import Redis
import copy


class RedisAggregator(BaseAggregator, BaseWorkerAggregator):
    worker_num = None
    agg_count = 0
    _redis = None

    def __init__(self, result_name, host, port, prefix, ttl, db=0, agg_size=100, remove_mode=False, **kwargs):
        super(RedisAggregator, self).__init__(result_name, remove_mode=remove_mode, **kwargs)
        self.host = host
        self.port = port
        self.db = db
        self.result_name = result_name
        self._prefix = prefix
        self.prefix = prefix + result_name + '_'
        self.ttl = ttl
        self.agg_dict = {}
        self.agg_size = agg_size
        self.workers = []
        if not remove_mode:
            self.redis.delete(self.prefix)

    @property
    def redis(self):
        if not self._redis:
            self._redis = Redis(host=self.host, port=self.port, db=self.db)
        return self._redis

    def __getstate__(self):
        odict = self.__dict__.copy()
        odict['_redis'] = None
        return odict

    def attach_to_worker(self, num):
        self.worker_num = num
        self.workers.append(num)
        worker_agg = copy.copy(self)
        worker_agg.agg_dict = {}
        return worker_agg

    def aggregate(self, word):
        word = word.lower()
        self.agg_count += 1
        v = self.agg_dict.get(word, 0)
        self.agg_dict[word] = v + 1
        if self.agg_count >= self.agg_size:
            self._send_agg_pack()
            self.agg_count = 0

    def _get_worker_border_key(self, num):
        return '%sborder_%s' % (self.prefix, num)

    def border_words(self, worker_num, first_word, last_word):
        key = self._get_worker_border_key(worker_num)
        pipe = self.redis.pipeline()
        pipe.hmset(key, {'first': first_word, 'last': last_word})
        pipe.expire(key, self.ttl)
        pipe.execute()

    def _send_agg_pack(self):
        if not self.agg_dict:
            return
        pipe = self.redis.pipeline()
        for key, value in self.agg_dict.items():
            if self.remove_mode:
                pipe.zrem(self.prefix, key)
            else:
                pipe.zincrby(self.prefix, key, value)
        pipe.expire(self.prefix, self.ttl)
        pipe.execute()
        self.agg_dict = {}

    def __exit__(self, ext, exv, trb):
        self._send_agg_pack()

    def finalize_results(self):
        pipe = self.redis.pipeline()
        for worker in self.workers:
            pipe.hmget(self._get_worker_border_key(worker), ['first', 'last'])
        self._aggregate_border_words(pipe.execute())
        self._send_agg_pack()
        i = 0
        result = True
        while result:
            result = self.redis.zrevrangebyscore(self.prefix, '+inf', '-inf', i * self.agg_size, self.agg_size,
                                                 withscores=True)
            i += 1
            for item in result:
                try:
                    item = (item[0].decode('utf-8'), item[1])
                except UnicodeError:
                    pass
                yield item
