import copy
import functools
import itertools
import logging
import operator
import time

import six

from . collections_ext import nameddict
from . itertools_ext import fxrange
from . rate_limits import truncated_exponential_backoff as teb

LOGGER = logging.getLogger(__name__)


class RetryDelaySeries(object):
    @classmethod
    def get(cls, name, **kwargs):
        return cls.definitions()[name](**kwargs)

    @classmethod
    def definitions(cls):
        return dict(
            truncated_exponential_backoff=cls.truncated_exponential_backoff,
            linear=cls.linear
        )

    @classmethod
    def truncated_exponential_backoff(cls, **kwargs):
        delay = kwargs.pop('delay')
        kwargs.setdefault('collision', 0)
        op = kwargs.pop('op', None)
        if isinstance(op, six.string_types):
            kwargs.update(op=getattr(operator, op))
        while True:
            yield teb(delay, **kwargs)
            kwargs['collision'] = kwargs['collision'] + 1

    @classmethod
    def linear(cls, **kwargs):
        params = dict(
            start=kwargs['delay'],
            stop=kwargs.get('max_delay', 0),
            step=kwargs['step'],
        )
        return fxrange(**params)


class HA(object):
    HA_CONFIG_KEY = 'ha_retry'
    DEFAULT_HA_CONFIG = dict(
        default=dict(
            delay=30,
            max_retries=0,
            delay_policy='truncated_exponential_backoff',
            delay_config=dict(
                max_collisions=5
            )
        )
    )

    def __init__(self, ha_config=None, retry_delays_class=None):
        if ha_config is None:
            import docido_sdk.config as config
            ha_config = config.get(
                HA.HA_CONFIG_KEY,
                nameddict(HA.DEFAULT_HA_CONFIG)
            )
        self.ha_config = ha_config
        self._retry_delays_class = retry_delays_class or RetryDelaySeries

    @classmethod
    def catch(cls, catch_exception, config='default'):
        """Decorator class method catching exceptions raised by the wrapped
        member function. When exception is caught, the decorator waits
        for an amount of time specified in the `ha_config`.

        :param catch_exception: Exception class or tuple of exception classes.
        """
        def wrap(method):
            @functools.wraps(method)
            def wrapped_method(self, *args, **kwargs):
                assert isinstance(self, HA)
                delay_policy = self.ha_get_delay_policy(config)
                max_retries = self.ha_get_config(config).max_retries
                for retries in itertools.count():
                    try:
                        return method(self, *args, **kwargs)
                    except catch_exception as e:
                        res = self.ha_on_error(method, e, *args, **kwargs)
                        if res is not None:
                            args, kwargs = res
                        if max_retries and retries >= max_retries:
                            raise
                        tts = next(delay_policy)
                        time.sleep(tts)
            return wrapped_method
        return wrap

    def ha_get_config(self, name):
        return self.ha_config[name]

    def ha_get_delay_policy(self, config_name):
        """Build generator of delays to wait between each call

        :param string config_name: configuration name
        """
        config = self.ha_get_config(config_name)
        delay_policy_conf = config.delay_config
        delay_policy_conf = copy.deepcopy(delay_policy_conf)
        delay_policy_conf.update(delay=config.delay)
        return self._retry_delays_class.get(
            config.delay_policy,
            **delay_policy_conf
        )

    def ha_on_error(self, method, exc, *args, **kwargs):
        """Callback when exception is caught by the Ha.catch decorator.
        This method is meant to be overloaded.

        :param method: the method that failed.
        :param tuple args: arguments given to the method
        :param dict kwargs: keyword arguments given to the method

        :return: tuple (args, **kwargs) to override the arguments given
        to the next attempt, `None` otherwise.
        """
        pass
