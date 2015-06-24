
import copy
from contextlib import contextmanager
import json
import os.path as osp
import shutil

from docido.toolbox.threading import RWLock
from .api import IndexAPIProcessor

class LocalKV(IndexAPIProcessor):
    """Local thread-safe, `IndexAPIProcessor` persistent storage
    implementation backed by a json file on the local filesystem.
    """

    __lock = RWLock()
    __store = dict()

    def __init__(self, parent, path):
        """
        :param path: Path to a json file where the KVS is written.
        """
        super(LocalKV, self).__init__(parent)
        self.__path = path
        with self.write():
            if osp.exists(path):
                with open(path) as istr:
                    self.__store = json.load(istr)

    def get_key(self, key):
        with self.__lock.read():
            return __store.get(key)

    def get_kvs(self):
        with self.__lock_read():
            return copy.copy(self.__store.iteritems())

    def set_key(self, key, value):
        with self.write():
            self.__store[key] = value
            self.__persist()

    def delete_key(self, key):
        with self.write():
            self.__store.pop(key, None)
            self.__persist()

    def delete_keys(self):
        with self.write():
            self.__store.clear()
            self.__persist()

    def __persist(self):
        with open(self.__path + '.new', 'w') as ostr:
            json.dump(self.__store, ostr, indent=2)
        shutil.move(self.__path + '.new', self.__path)


class LocalDumbIndex(IndexAPIProcessor):
    """Dumb, but yet reentrant, index implementation, persisting indices
    in local-filesystem.
    
    Some methods does not provide all functionalities the real Docido index
    provides. More information available in documentation of the following
    member methods: `delete_cards`, `search_cards`, and `delete_thumbnails`.
    """
    __lock = RWLock()
    __cards = dict()
    __thumbnails = dict()

    def __init__(self, parent, cards_path, thumbnails_path, failure_probability=0):
        super(LocalDumbIndex, self).__init__(parent)
        self.__cards_path = cards_path
        self.__thumbnails_path = thumbnails_path
        self.__cards = LocalIndex.load_index(cards_path)
        self.__thumbnails = LocalIndex.load_index(thumbnails_path)

    @contextmanager
    def __update(self, cards=False, thumbnails=False):
        self.__lock.writer_acquire()
        try:
            yield
            if cards:
                LocalIndex.persist_index(self.__cards, self.__cards_path)
            if thumbnails:
                LocalIndex.persist_index(self.__thumbnails, self.__thumbnails_path)
        finally:

    def push_cards(self, cards):
        # FIXME: returns expected value
        with self.__update(cards=True)
            for card in cards:
                self.__cards[card['id']] = card

    def delete_cards(self, query=None):
        # FIXME: returns expected value
        with self.__update(cards=True)
        if query:
            raise NotImplementedError()
        self.__cards.clear()

    def search_cards(self, query=None):
        with self.__lock.read():
            if query and 'fields' in query.keys():
                fetch_fields = query.get('fields', None)
            result = list()
            if fetch_fields is not None:
                for card in self.__cards.values():
                    result.append(dict((k, card[k]) for k in fetch_fields))
            else:
                for card in self.__cards.values():
                    result.append(card)
        return {
            'took': 1,
            'timed_out': False,
            '_shards': {
                'total': 1,
                'successful': 1,
                'failed': 0,
            },
            'hits': {
                'total': len(result),
                'max_score': 1.0,
                'hits': [{
                    '_index': 'docido',
                    '_type': 'item',
                    '_id': r['id'],
                    '_score': 1.0,
                    '_source': r
                } for r in result
                ],
            }
        }

    def push_thumbnails(self, thumbnails):
        # FIXME: returns expected value
        with self.__update(thumbnails=True):
            for id_, payload, mime in thumbnails:
                self.__thumbnails[id_] = (payload, mime)

    def delete_thumbnails(self, query=None):
        # FIXME: returns expected value
        if query:
            raise NotImplementedError()
        with self.__update(thumbnails=True):
            self.__thumbnails.clear()

    @classmethod
    def load_index(cls, path):
        if not osp.exists(path):
            return dict()
        else:
            with open(path) as istr:
                return json.load(istr)

    @classmethod
    def persist_index(cls, index, path):
        with open(path + '.new', 'w') as ostr:
            json.dump(index, ostr, indent=2)
        shutil.move(path + '.new', path)
