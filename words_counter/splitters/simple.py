from base import BaseSplitter


class SimpleSplitter(BaseSplitter):
    def _split_buffer(self, str_buffer):
        last_pos = -1
        length = len(str_buffer)
        for i in range(length):
            if not str_buffer[i].isalpha():
                if i > last_pos + 1:
                    yield str_buffer[last_pos + 1:i]
                last_pos = i
        self.buffer_empty = True
        if last_pos + 1 < length:
            yield str_buffer[last_pos + 1:length]

    def _starts_with_word(self, str_buffer):
        return str_buffer and str_buffer[0].isalpha()

    def _finished_with_word(self, str_buffer):
        return str_buffer and str_buffer[-1].isalpha()
