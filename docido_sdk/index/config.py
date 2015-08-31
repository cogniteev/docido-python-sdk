
import os
import os.path as osp

import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

from docido_sdk.core import (
    Component,
    ExtensionPoint,
    implements,
)
from docido_sdk.toolbox.decorators import lazy
from . api import (
    IndexAPIProvider,
    IndexPipelineConfig,
    PullCrawlerIndexingConfig,
)


class YamlPullCrawlersIndexingConfig(Component):
    implements(PullCrawlerIndexingConfig, IndexPipelineConfig)
    index_api_providers = ExtensionPoint(IndexAPIProvider)

    def service(self, service):
        crawlers_config = self._config['pull_crawlers']['crawlers']
        if service not in crawlers_config:
            raise Exception("Cannot find config for crawler " + service)
        return crawlers_config[service].get('indexing', {})

    def core(self):
        return self._config['pull_crawlers']['indexing']

    def get_pipeline(self):
        indexing_config = self.core()
        processor_pipeline = indexing_config['pipeline']
        providers = dict([
            (p.__class__.__name__, p)
            for p in list(self.index_api_providers)
        ])
        return list(map(lambda p: providers[p], processor_pipeline))

    @classmethod
    def _from_file(cls, config_file):
        if not osp.exists(config_file) and not config_file.startswith('/'):
            path = os.path.dirname(os.path.abspath(__file__))
            config_file = '/'.join((path, config_file))
        with open(config_file, 'r') as conf:
            return yaml.load(conf, Loader=Loader)

    @lazy
    def _config(self):
        config_file = os.getenv('DOCIDO_CONFIG', 'settings.yml')
        return YamlPullCrawlersIndexingConfig._from_file(config_file)
