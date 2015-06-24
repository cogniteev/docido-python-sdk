
class IndexAPI:
    """Read/write access to Docido index. A `IndexAPI` can manipulate 3 kind of data:

    - cards: a searchable item in Docido index.
    - thumbnails: a binary item in Docido index, for thumbnails of 
    card's attachments. Used to improve user-experience by providing fast preview
    of binary files attached to cards. 
    - a key value store: provides crawlers a way to persist their synchronization
    state.

    Error handling:
    every bulk operation that modifies Docido index returns the list of 
    operations that failed. Every item is a `dict` providing the following key:
      - status: http error code
      - error: reason in string format
      - id: error identifier
      - card: original card

    Filtering:
    Index enumeration and deletion operations allow you to restrict 
    the target scope by providing a `query` in parameter.
    The `query` parameters follows the Elasticsearch Query DSL.
    """
    def push_cards(self, cards):
        """Send a synchronous bulk indexing request

        :arg cards: collections of cards to index.
        :return collection of items whose insertion failed.
        """
        pass

    def delete_cards(self, query=None):
        """Send a synchronous bulk deletion request

        :arg query: a search definition using the Elasticsearch Query DSL
        to restrict the scope of cards to delete.
        :return collection of items whose deletion failed.
        """
        pass

    def search_cards(self, query=None):
        """Enumerate cards in Docido index.

        :arg query: a search definition using the Elasticsearch Query DSL
        :return FIXME
        """
        pass

    def push_thumbnails(self, thumbnails):
        """Add or update thumbnails in dedicated Docido index.

        :arg thumbnails: Collection of tuples
        `(identifier, encoded_bytes, mime_type)`
        :return collection of items whose insertion failed.
        """
        pass

    def delete_thumbnails(self, query=None):
        """Delete thumbnails from dedicated Docido index.

        :arg query: a search definition using the Elasticsearch Query DSL to 
        restrict the scope of thumbnails to delete.
        :return collection of items whose deletion failed.
        """
        pass

    def get_key(self, key):
        pass

    def set_key(self, key, value):
        pass

    def delete_key(self, key):
        """Remove key from persistent storage.

        :arg key: the key to remove
        """

    def delete_keys(self):
        pass

    def get_kvs(self):
        pass

    def ping(self):
        pass


class IndexAPIProcessor(IndexAPI):
    def __init__(self, parent):
        self.__parent = parent

    def push_cards(self, cards):
        return self.__parent.push_cards(cards)

    def delete_cards(self, query=None):
        return self.__parent.delete_cards(query)

    def search_cards(self, query=None):
        return self.__parent.search_cards(query)

    def push_thumbnails(self, thumbnails):
        return self.__parent.push_thumbnails(thumbnails)

    def delete_thumbnails(self, query=None):
        return self.__parent.delete_thumbnails(query)

    def get_key(self, key):
        return self.__parent.get_key(key)

    def set_key(self, key, value):
        return self.__parent.set_key(key, value)

    def delete_key(self, key):
        return self.__parent.delete_key(key)

    def delete_keys(self):
        return self.__parent.delete_keys()

    def get_kvs(self):
        return self.__parent.get_kvs()

    def ping(self):
        return self.__parent.ping()
