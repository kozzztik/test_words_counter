from base import BaseWorkerAggregator, BaseAggregator
from multiprocessing import Queue


class DictWorkerAggregator(BaseWorkerAggregator):
    def __init__(self, queue):
        """

        :param Queue queue: output queue
        """
        self.queue = queue
        self.border_first = None
        self.border_last = None
        self.agg = {}

    def aggregate(self, word):
        word = word.lower()
        v = self.agg.get(word, 0)
        self.agg[word] = v + 1

    def border_words(self, worker_num, first_word, last_word):
        self.border_first = first_word
        self.border_last = last_word

    def __exit__(self, ext, exv, trb):
        self.queue.put({"first": self.border_first, "last": self.border_last, "agg": self.agg})


class DictAggregator(BaseAggregator):
    def __init__(self, result_name, remove_mode=False, **kwargs):
        super(DictAggregator, self).__init__(result_name, remove_mode, **kwargs)
        self.workers = {}
        self.agg = {}

    def aggregate(self, word, count=1):
        word = word.lower()
        v = self.agg.get(word, 0)
        self.agg[word] = v + count

    def sort_kwargs(self):
        return {'key': lambda x: x[1]}

    def finalize_results(self):
        border_data = []
        keys = self.workers.keys()
        keys.sort()
        for worker in keys:
            data = self.workers[worker].get()
            border_data.append((data['first'], data['last']))
            for key, value in data['agg'].items():
                self.aggregate(key, value)
        self._aggregate_border_words(border_data)
        return sorted(self.agg.items(), reverse=True, **self.sort_kwargs())

    def attach_to_worker(self, num):
        q = Queue()
        self.workers[num] = q
        return DictWorkerAggregator(q)


class StrongSortedDictAggregator(DictAggregator):
    def sort_kwargs(self):
        return {'cmp': lambda x, y: cmp(x[1], y[1]) or cmp(x[0], y[0])}
