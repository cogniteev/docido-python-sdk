.. _api:

Developer Interface
===================

.. module:: docido

This part of the documentation covers all the interfaces of Docido Python SDK.

Index API
----------

.. autoclass:: docido.index.IndexAPI
   :inherited-members:
.. autoclass:: docido.index.IndexAPIProcessor
   :inherited-members:

Crawler API
-----------

Introspection
~~~~~~~~~~~~~~

.. autoclass:: docido.crawler.api.ICrawler
   :inherited-members:
.. autoclass:: docido.crawler.api.CrawlConfiguration
   :inherited-members:
.. autoclass:: docido.crawler.api.ICrawlerManager
   :inherited-members:

Oauth
~~~~~

.. autoclass:: docido.oauth.api.OAuthToken
   :inherited-members:
.. autoclass:: docido.oauth.api.OAuthExpiresToken
   :inherited-members:
.. autoclass:: docido.oauth.api.OAuthRefreshToken
   :inherited-members:
.. autoclass:: docido.oauth.api.OAuthSecretToken
   :inherited-members:
