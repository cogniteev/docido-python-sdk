---
title: Crawler Source Code
tags: [getting-started]
keywords: crawlers, development
last_updated: November 23, 2015
summary: "Describes crawler source code layout, and development process"
---

## Git branching model

Crawler projects follow the [Git Flow](http://danielkummer.github.io/git-flow-cheatsheet/).
There is no particular good reason to do that, except that at least one common
workflow is required.

To summarize the workflow:

1. Crawler developers push to the develop branch
1. When ready, integrators creates a `release/vX.X` branch and deploy,
and iterate until version is good for production.
1. Integrators merge the `release/vX.X` branch on the master branch, and tag it.

## Project layout

Crawler repositories are all based on a template project owned by Cogniteev
core developers. When the template is modified, changes are dispatched on all
crawlers, so stay tune!

A crawler project provides, among others, the following files:

* `Dockerfile`: to build the Docker image used by Docido application.
* `requirements-dev.txt`: provides additional Python packages required to test
the crawler.
* `tox.ini`: `tox` configuration file, see **Validate your changes** section
below.
* `settings.yml`: `dcc-run` environment configuration
* `settings-es.yml`: `dcc-run` utility input file, for crawlers that need
Elasticsearch to run properly.
* `.dcc-runs.yml`: `dcc-run` input file, providing crawls configuration.

## Bootstrap development environment

You may use `tox` to ensure that your pull-crawler source code is sane.
Run the following commands to bootstrap your development environment:

```
git clone .../docido-pull-crawler-foo.git
cd docido-pull-crawler-foo
virtualenv .env
. .env/bin/activate
pip install tox
tox
```

## Requirements

You may test your development against Python 2.7.9

{{site.data.alerts.tip}} You can increase quality of your code by testing it
against several Python versions by adding them in tox.ini
{{site.data.alerts.end}}

## Validate your changes

Before pushing change to the `develop` branch, you must ensure that the `tox`
command works properly. This command executed:

* unit-tests
* unit-tests coverage. There is no minimum percentage required, but you may
**ensure that it never decreases !**
* check source code compliancy against PEP8 standards
