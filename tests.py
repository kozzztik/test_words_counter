import unittest
import os
from words_counter.processor import CounterProcessor
from words_counter.sources.base import StringSource
from words_counter.sources.file_source import FileSource
from words_counter.sources.http_source import HTTPSource
from words_counter.splitters.simple import SimpleSplitter
from words_counter.splitters.regexp_splitter import RegexpSplitter
from words_counter.workers.base import SimpleWorker
from words_counter.workers.threads import ThreadWorker
from words_counter.workers.multiprocessor import ProcessWorker
from words_counter.workers.celery_worker import CeleryWorker
from words_counter.aggregators.redis_aggr import RedisAggregator
from words_counter.aggregators.dict_aggr import StrongSortedDictAggregator
import settings


class AuthBackendTestCase(unittest.TestCase):
    _test_url = 'http://kozzz.ru'
    _test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_text.txt')
    
    def setUp(self):
        self.source_class = FileSource
        processor = CounterProcessor(self.source_class, SimpleWorker, RedisAggregator, SimpleSplitter)
        self.base_results = list(processor.count_words(self._test_file, 'results', 1, 1024 * 1024, settings))

    def _check_results(self, results, base_results=None):
        base_results = base_results or self.base_results
        self.assertEqual(len(results), len(base_results), 'Different results length')
        for base_result, new_result in zip(base_results, results):
            base_key, base_value = base_result
            key, value = new_result
            self.assertEqual(base_key, key, 'Keys on one place are different (%s, %s)' % (base_key, key))
            self.assertEqual(base_value, value, 'Keys values are different on key %s' % key)

    def test_concurrency(self):
        processor = CounterProcessor(self.source_class, SimpleWorker, RedisAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 1024 * 1024, settings))
        self._check_results(results)

    def test_buffering(self):
        processor = CounterProcessor(self.source_class, SimpleWorker, RedisAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 1, 128, settings))
        self._check_results(results)

    def test_concurrency_and_buffering(self):
        processor = CounterProcessor(self.source_class, SimpleWorker, RedisAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)

    def test_threads(self):
        processor = CounterProcessor(self.source_class, ThreadWorker, RedisAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)

    def test_processes(self):
        processor = CounterProcessor(self.source_class, ProcessWorker, RedisAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)

    def test_celery_worker(self):
        processor = CounterProcessor(self.source_class, CeleryWorker, RedisAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)

    def test_http_source(self):
        processor = CounterProcessor(HTTPSource, ProcessWorker, RedisAggregator, SimpleSplitter)
        base_results = list(processor.count_words(self._test_url, 'results', 1, 1024 * 1024, settings))
        results = list(processor.count_words(self._test_url, 'results', 6, 1024, settings))
        self._check_results(results, base_results)

    def test_regexp_splitter(self):
        processor = CounterProcessor(self.source_class, SimpleWorker, RedisAggregator, RegexpSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)

    def test_string_source(self):
        l = FileSource.source_size(self._test_file)
        with FileSource(self._test_file, 0, l, l) as f:
            data = f.next()
        processor = CounterProcessor(StringSource, SimpleWorker, RedisAggregator, RegexpSplitter)
        results = list(processor.count_words(data, 'results', 6, 128, settings))
        self._check_results(results)

    def test_remove_mode(self):
        processor = CounterProcessor(StringSource, SimpleWorker, RedisAggregator, RegexpSplitter)
        processor.count_words('na v ot nah pod k za v na', 'results', 1, 128, settings)
        results = list(processor.count_words('ot na pod za na ot na', 'results', 1, 128, settings, remove_mode=True))
        self.assertEqual(len(results), 3, 'Bad results length')
        self.assertEqual(results[0], ('v', 2.0))
        self.assertEqual(results[1], ('nah', 1.0))
        self.assertEqual(results[2], ('k', 1.0))

    def test_dict_aggr_multi_proc(self):
        processor = CounterProcessor(self.source_class, ProcessWorker, StrongSortedDictAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)

    def test_dict_aggr_threads(self):
        processor = CounterProcessor(self.source_class, ThreadWorker, StrongSortedDictAggregator, SimpleSplitter)
        results = list(processor.count_words(self._test_file, 'results', 6, 128, settings))
        self._check_results(results)


if __name__ == '__main__':
    unittest.main()
