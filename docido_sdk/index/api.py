
from docido_sdk.core import Interface

__all__ = ['IndexAPI']


class IndexAPI(Interface):
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
    def push_cards(cards):
        """Send a synchronous bulk indexing request

        :param list cards: collections of cards to index.

        :return: collection of items whose insertion failed.
        """

    def delete_cards(query=None):
        """Send a synchronous bulk deletion request.

        :param list query: a search definition using the Elasticsearch
            Query DSL to restrict the scope of cards to delete.

        :return: collection of items whose deletion failed.
        """

    def search_cards(query=None):
        """Enumerate cards in Docido index.

        :param list query: a search definition using the
            Elasticsearch Query DSL

        :return: FIXME
        """

    def push_thumbnails(thumbnails):
        """Add or update thumbnails in dedicated Docido index.

        :param list thumbnails: Collection of tuples
                                `(identifier, encoded_bytes, mime_type)`

        :return: collection of items whose insertion failed.
        """

    def delete_thumbnails(query=None):
        """Delete thumbnails from dedicated Docido index.

        :param query: a search definition using the Elasticsearch Query DSL to
                    restrict the scope of thumbnails to delete.

        :return: collection of items whose deletion failed.
        """

    def get_kv(key):
        """Retrieve value from persistence layer

        :param string key: input key

        :return: the value is present, `None` otherwise.
        :rtype: string
        """

    def set_kv(key, value):
        """Insert or update existing key in persistence layer.

        :param string key: input key
        :param string value: value to store
        """

    def delete_kv(key):
        """Remove key from persistent storage.

        :param key: the key to remove
        """

    def delete_kvs():
        """Remove all crawler persisted data.
        """

    def get_kvs():
        """Retrieve all crawler persisted data.

        :return: collection of tuple `(key, value)`
        :rtype: list
        """

    def ping():
        """Test availability of Docido index

        :raises SystemError: if Docido index is unreachable
        """

    def refresh_oauth_access_token():
        """Refresh OAuth access token.
        This method may be used when the crawled source
        invalidates the OAuth access token.

        :return: new access token
        :rtype: basestring
        """
