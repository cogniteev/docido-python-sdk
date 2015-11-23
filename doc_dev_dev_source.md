---
title: Crawler Source Code
tags: [getting-started]
keywords: crawlers, development
last_updated: November 23, 2015
summary: ""
---

Describes crawler source code layout


## Development environment

### Bootstrap

You may use `tox` to ensure that your pull-crawler source code is sane. Run the following commands to bootstrap your development environment:

```
$ virtualenv .env
$ . .env/bin/activate
$ pip install tox
```

### Validate your changes

Before pushing change to the `develop` branch, you must ensure that the `tox` command works properly, that execute:

* unit-tests
* unit-tests coverage (no minimum percentage required)
* check source code compliancy against PEP8 standards
