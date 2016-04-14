from words_counter.processor import CounterProcessor
from words_counter.splitters.simple import SimpleSplitter
from words_counter.workers.multiprocessor import ProcessWorker
import settings
import time
import os
import getopt
import sys
help_str = 'counter_app.py -i <input_file> -r <reference_file> -c <concurrency> -b <read_buffer_size> ' \
           '-a <aggregation_size>'
path1 = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_text.txt')
concurrency = settings.concurrency
read_buffer = settings.read_buffer_size
path2 = None
try:
    opts, args = getopt.getopt(sys.argv[1:len(sys.argv)], "hi:o:c:r:b:a", ["help"])
except getopt.GetoptError:
    print help_str
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h", "--help"):
        print help_str
        sys.exit()
    elif opt == "-i":
        path1 = arg
    elif opt == "-r":
        path2 = arg
    elif opt == "-c":
        concurrency = int(arg)
    elif opt == '-b':
        read_buffer = int(arg)
    elif opt == '-a':
        settings.aggregator['agg_size'] = int(arg)
    else:
        print "Unknown command line argument: %s" % opt
        sys.exit(2)

processor = CounterProcessor(settings.source_class, ProcessWorker, settings.aggregator_class,
                             SimpleSplitter)
start_time = time.time()
results = processor.count_words(path1, concurrency, read_buffer, settings)
if path2:
    results = processor.count_words(path2, concurrency, read_buffer, settings,
                                    agg_data=processor.aggregator.agg, remove_mode=True)
result_time = time.time() - start_time

for name, value in results:
    print "%s: %s" % (name, value)
print
print "Processed in %s seconds" % result_time
