from base import BaseWorkerAggregator, BaseAggregator
from multiprocessing import Queue, Event, Lock
from threading import Thread


class DictWorkerAggregator(BaseWorkerAggregator):
    def __init__(self, num, queue, lock, sync_event, size_limit):
        self.queue = queue
        self.lock = lock
        self.sync_event = sync_event
        self.border_first = None
        self.border_last = None
        self.agg = {}
        self.num = num
        self.size_limit = size_limit
        self.size = 0

    def aggregate(self, word):
        word = word.lower()
        v = self.agg.get(word, 0)
        if not v:
            self.size += 1
        self.agg[word] = v + 1
        if self.size >= self.size_limit:
            self.send_data()

    def send_data(self):
        with self.lock:
            self.sync_event.clear()
            self.queue.put({"first": self.border_first, "last": self.border_last, "agg": self.agg, 'num': self.num})
            self.sync_event.wait()
        self.agg.clear()
        self.size = 0

    def border_words(self, worker_num, first_word, last_word):
        self.border_first = first_word
        self.border_last = last_word

    def __exit__(self, ext, exv, trb):
        if self.agg:
            self.send_data()


class SyncThread(Thread):
    def __init__(self, aggregator):
        super(SyncThread, self).__init__()
        self.sync_event = Event()
        self.finish_event = Event()
        self.sync_lock = Lock()
        self.aggregator = aggregator
        self.queue = Queue()

    def run(self):
        while (not self.finish_event.is_set()) or (not self.queue.empty()):
            obj = self.queue.get()
            if obj:
                self.aggregator.aggregate_worker_data(obj)
                self.sync_event.set()


class DictAggregator(BaseAggregator):
    def __init__(self, remove_mode=False, agg_size=100, **kwargs):
        super(DictAggregator, self).__init__(remove_mode, **kwargs)
        self.workers = {}
        self.sync_thread = SyncThread(self)
        self.sync_thread.start()
        self.agg_size = agg_size

    def aggregate(self, word, count=1):
        if self.remove_mode:
            if word in self.agg:
                del self.agg[word]
        else:
            word = word.lower()
            v = self.agg.get(word, 0)
            self.agg[word] = v + count

    def sort_kwargs(self):
        return {'key': lambda x: x[1]}

    def aggregate_worker_data(self, data):
        num = data['num']
        self.workers[num]['first'] = data['first']
        self.workers[num]['last'] = data['last']
        for key, value in data['agg'].items():
            self.aggregate(key, value)

    def finalize_results(self):
        self.sync_thread.finish_event.set()
        self.sync_thread.queue.put(None)
        self.sync_thread.join()
        keys = self.workers.keys()
        keys.sort()
        self._aggregate_border_words([(self.workers[num]['first'], self.workers[num]['last']) for num in keys])
        return sorted(self.agg.items(), reverse=True, **self.sort_kwargs())

    def attach_to_worker(self, num):
        self.workers[num] = {'first': None, 'last': None}
        return DictWorkerAggregator(num, self.sync_thread.queue, self.sync_thread.sync_lock,
                                    self.sync_thread.sync_event, self.agg_size)


class StrongSortedDictAggregator(DictAggregator):
    def sort_kwargs(self):
        return {'cmp': lambda x, y: cmp(x[1], y[1]) or cmp(x[0], y[0])}
