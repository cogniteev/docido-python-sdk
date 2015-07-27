
__all__ = ['IndexAPI', 'IndexAPIProcessor']


class IndexAPI:
    """Read/write access to Docido index.

    :An IndexAPI object can manipulate 3 kind of data:
        :cards:
          a searchable item in Docido index.
        :thumbnails:
          a binary item in Docido index, for thumbnails of
          card's attachments. Used to improve user-experience by providing
          fast preview of binary files attached to cards.
        :a key value store:
          provides crawlers a way to persist their synchronization state.

    :Error Handling:
        Every bulk operation that modifies Docido index returns the list of
        operations that failed. Every item is a `dict` providing
        the following key:

        :status:
          http error code
        :error:
          reason in string format
        :id:
          error identifier
        :card:
          original card

    :Filtering:
        Index enumeration and deletion operations allow you to restrict
        the target scope by providing a `query` in parameter.
        The `query` parameters follows the Elasticsearch Query DSL.
    """
    def push_cards(self, cards):
        """Send a synchronous bulk indexing request

        :param list cards: collections of cards to index.

        :return: collection of items whose insertion failed.
        """
        pass

    def delete_cards(self, query=None):
        """Send a synchronous bulk deletion request.

        :param list query: a search definition using the Elasticsearch
            Query DSL to restrict the scope of cards to delete.

        :return: collection of items whose deletion failed.
        """
        pass

    def search_cards(self, query=None):
        """Enumerate cards in Docido index.

        :param list query: a search definition using the
            Elasticsearch Query DSL

        :return: FIXME
        """
        pass

    def push_thumbnails(self, thumbnails):
        """Add or update thumbnails in dedicated Docido index.

        :param list thumbnails: Collection of tuples
                                `(identifier, encoded_bytes, mime_type)`

        :return: collection of items whose insertion failed.
        """
        pass

    def delete_thumbnails(self, query=None):
        """Delete thumbnails from dedicated Docido index.

        :param query: a search definition using the Elasticsearch Query DSL to
                    restrict the scope of thumbnails to delete.

        :return: collection of items whose deletion failed.
        """
        pass

    def get_kv(self, key):
        """Retrieve value from persistence layer

        :param string key: input key

        :return: the value is present, `None` otherwise.
        :rtype: string
        """
        pass

    def set_kv(self, key, value):
        """Insert or update existing key in persistence layer.

        :param string key: input key
        :param string value: value to store
        """
        pass

    def delete_kv(self, key):
        """Remove key from persistent storage.

        :param key: the key to remove
        """

    def delete_kvs(self):
        """Remove all crawler persisted data.
        """
        pass

    def get_kvs(self):
        """Retrieve all crawler persisted data.

        :return: collection of tuple `(key, value)`
        :rtype: list
        """
        pass

    def ping(self):
        """Test availability of Docido index

        :raises SystemError: if Docido index is unreachable
        """
        pass

    def refresh_oauth_access_token(self):
        """Refresh OAuth access token.
        This method may be used when the crawled source
        invalidates the OAuth access token.

        :return: new access token
        :rtype: basestring
        """


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
