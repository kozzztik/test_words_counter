from words_counter.sources.file_source import FileSource
from words_counter.splitters.simple import SimpleSplitter
from words_counter.workers.base import SimpleWorker
from words_counter.aggregators.redis_aggr import RedisAggregator
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

source_class = FileSource
splitter_class = SimpleSplitter
worker_class = SimpleWorker
aggregator_class = RedisAggregator

source_path = os.path.join(BASE_DIR, 'test_text.txt')

concurrency = 3
read_buffer_size = 1024

aggregator = {
    'host': 'localhost',
    'port': '6379',
    'prefix': 'word_counter_',
    'ttl': 60 * 60,
    'agg_size': 10000
}

CELERY_SETTINGS = {
    'BROKER_URL': 'redis://localhost:6379/11',
    'CELERY_ACCEPT_CONTENT': ['pickle', 'json'],
    'CELERY_IMPORTS': ['words_counter.workers.celery_worker'],
    'CELERY_RESULT_BACKEND': 'redis://localhost:6379/13',
}
