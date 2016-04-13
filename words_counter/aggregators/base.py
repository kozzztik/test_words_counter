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
    def __init__(self, result_name, remove_mode=False, **kwargs):
        self.result_name = result_name
        self.kwargs = kwargs
        self.remove_mode = remove_mode

    def finalize_results(self):
        """
        Return iterable of result tuples ordered by descending count
        :return:
        """
        raise NotImplementedError

    def attach_to_worker(self, num):
        raise NotImplementedError
