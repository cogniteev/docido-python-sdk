# Docido Python SDK

[![Build Status](https://travis-ci.org/cogniteev/docido-python-sdk.svg)](https://travis-ci.org/cogniteev/docido-python-sdk)
[![Coverage Status](https://coveralls.io/repos/cogniteev/docido-python-sdk/badge.svg?branch=master&service=github)](https://coveralls.io/github/cogniteev/docido-python-sdk?branch=master)
[![Code Climate](https://codeclimate.com/github/cogniteev/docido-python-sdk/badges/gpa.svg)](https://codeclimate.com/github/cogniteev/docido-python-sdk)
[![Code Health](https://landscape.io/github/cogniteev/docido-python-sdk/master/landscape.svg?style=plastic)](https://landscape.io/github/cogniteev/docido-python-sdk/master)

# Installation

```shell
$ pip install docido-sdk
```

# Tests

You can use `tox` to run the test-suite on every supported platform:

```shell
# Install and load virtualenv
$ pip install virtualenv
$ virtualenv .env
$ .env/bin/activate
# Install tox
$ pip install tox
# Run the test suites
$ tox
```

The test-suite needs an Elasticsearch node to be up and running. You can provide `tox` the `ELASTICSEARCH_HOST` environment variable to override the default location, for instance:

```shell
$ export ELASTICSEARCH_HOST=foo.bar:9200
$ tox
```


# Issues

Pull-requests are welcome. You can also submit your issues to the
[issues tracker](https://github.com/cogniteev/docido-python-sdk/issues)

# License

Docido python SDK is licensed under the Apache License, Version 2.0.
See [LICENSE](LICENSE) file for full license text.
