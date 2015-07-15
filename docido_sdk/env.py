
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

    def setup(self):
        from docido_sdk.loader import load_components
        load_components(self)

env = Environment()
