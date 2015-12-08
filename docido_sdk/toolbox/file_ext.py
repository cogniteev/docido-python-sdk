from contextlib import closing
try:
    from cStringIO import StringIO
except ImportError:  # flake8: noqa
    from StringIO import StringIO


class iterator_to_file(object):
    """Incomplete implementation of a file-like object on top of
    an iterator.
    """
    def __init__(self, it):
        self._it = it
        self._buf = ''

    def __iter__(self):
        return self

    def close(self):
        pass

    def read(self, size=-1):
        if size >= 0:
            return self._read_n(size)
        else:
            with closing(StringIO()) as res:
                buf = self._read_n(4096)
                res.write(buf)
                while len(buf) == 4096:
                    buf = self._read_n(4096)
                    res.write(buf)
                return res.getvalue()

    def _read_n(self, size):
        while len(self._buf) < size:
            try:
                data = self.next()
            except StopIteration:
                if len(self._buf) == 0:
                    return ''
                else:
                    res = self._buf
                    self._buf = ''
                    return res
            self._buf += data
            if len(data) == 0:
                break
        if len(self._buf) > size:
            res = self._buf[:size]
            self._buf = self._buf[size:]
        else:
            len(self._buf)
            res = self._buf
            self._buf = ''
        return res

    def next(self):
        return self._it.next()
