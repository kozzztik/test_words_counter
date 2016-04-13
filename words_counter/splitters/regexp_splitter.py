from base import BaseSplitter
import re

r = re.compile(r"[^\W\d_]+", re.UNICODE)

class RegexpSplitter(BaseSplitter):
    def _split_buffer(self, str_buffer):
        for i in r.finditer(str_buffer):
            yield i.group()

    def _starts_with_word(self, str_buffer):
        return str_buffer and str_buffer[0].isalpha()

    def _finished_with_word(self, str_buffer):
        return str_buffer and str_buffer[-1].isalpha()
