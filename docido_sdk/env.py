
import logging

from docido_sdk.core import *


class Environment(Component, ComponentManager):
    """Docido SDK environment manager."""

    def __init__(self):
        ComponentManager.__init__(self)
        self.log = logging.getLogger()

    def component_activated(self, component):
        """Initialize additional member variables for components.

        Every component activated through the `Environment` object
        gets an additional member variable: `env` (the environment object)
        """
        component.env = self
        super(Environment, self).component_activated(component)

    def get_index_api(self, service, user_id, account_login):
        """Provides `IndexAPI` dedicated to a crawl

        :param basestring service:
          service name
        :param basestring user_id:
          Docido user identifier
        :param basestring account_login:
          Docido service account login
        :return: index API to be used by the crawl
        :rtype: :py:class:`docido_sdk.index.IndexAPI`
        """
        # FIXME

    def setup(self):
        from docido_sdk.loader import load_components
        load_components(self)

env = Environment()
