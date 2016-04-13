from words_counter.processor import CounterProcessor
import settings
import time
from words_counter.splitters.simple import SimpleSplitter
from words_counter.splitters.regexp_splitter import RegexpSplitter
from words_counter.workers.base import SimpleWorker
from words_counter.workers.threads import ThreadWorker
from words_counter.workers.multiprocessor import ProcessWorker
from words_counter.workers.celery_worker import CeleryWorker
import os
path1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'book1.txt')
path2 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'book2.txt')
processor = CounterProcessor(settings.source_class, ProcessWorker, settings.aggregator_class,
                             SimpleSplitter)
start_time = time.time()
processor.count_words(path1, 'results', 6, 1024 * 5, settings)
results = processor.count_words(path2, 'results', 6, 1024 * 5, settings, remove_mode=True)
result_time = time.time() - start_time

for name, value in results:
    print "%s: %s" % (name, value)
print
print "Processed in %s seconds" % result_time

# Simple splitter
# Threads: 50.89s