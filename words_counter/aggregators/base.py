class BaseWorkerAggregator(object):
    def aggregate(self, word):
        raise NotImplementedError

    def border_words(self, worker_num, first_word, last_word):
        raise NotImplementedError

    def __enter__(self):
        # open context here if needed
        return self

    def __exit__(self, ext, exv, trb):
        # close context here if needed
        pass


class BaseAggregator(object):
    def __init__(self, remove_mode=False, agg_data=None, **kwargs):
        self.kwargs = kwargs
        self.remove_mode = remove_mode
        self.agg = agg_data or {}

    def aggregate(self, word):
        raise NotImplementedError

    def _aggregate_border_words(self, data):
        prev_last_word = None
        while data:
            first_word, last_word = data.pop(0)
            if first_word and prev_last_word:
                self.aggregate(prev_last_word + first_word)
            elif first_word or prev_last_word:
                self.aggregate(first_word or prev_last_word)
            prev_last_word = last_word
        if prev_last_word:
            self.aggregate(prev_last_word)

    def finalize_results(self):
        """
        Return iterable of result tuples ordered by descending count
        :return:
        """
        raise NotImplementedError

    def attach_to_worker(self, num):
        raise NotImplementedError
