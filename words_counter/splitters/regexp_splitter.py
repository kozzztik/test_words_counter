from base import BaseSplitter
import re


class RegexpSplitter(BaseSplitter):
    def _split_buffer(self, str_buffer):
        return re.sub('\W', ' ', str_buffer).split()

    def _starts_with_word(self, str_buffer):
        return str_buffer and str_buffer[0].isalpha()

    def _finished_with_word(self, str_buffer):
        return str_buffer and str_buffer[-1].isalpha()
