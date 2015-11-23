---
title: Components Development Testing
keywords: component, development, testing
last_updated: November 23, 2015
summary: ""
---

## Run a crawl on your workstation

In order to run the crawl locally, a command is exposed by the docido SDK and available once its installed through `pip`. The dependency should lay in the crawler's ```setup.py``` and be of the following form ```'docido-sdk>=x.y.z'```, then the sdk is to be installed by running ```$ pip install -U .``` don't forget to update the shell paths via ```$ hash -r``` to use it right away.

The script relies on two configuration files to build the proper testing environment:

* Global YAML configuration, describing the crawler's environment (Index API pipeline, extra schemas to check, extra fields to add to the elasticsearch mapping...). There are 2 basic configurations:
  * `settings.yml`: the most simple one, without required 3rd parties. Items pushed by your crawler are stored locally.
  * `settings-es.yml`: Describe environment where documents emitted by your crawler are stored in Elasticsearch. This configuration is required when your crawl needs to execute Elasticsearch queries to perform its incremental scan.
* ```.dcc-runs.yml``` describing the crawls to launch.

By default, `settings.yml` is used as default crawler environment. If your crawler needs Elasticsearch, then you can specify another YAML configuration file in `.dcc-runs.yml`

Once the SDK is installed and the configuration files filled, the crawl can be run locally via the ```dcc-run``` command, some options can be specified:

* `-v|vv|vvv the` verbosity level of the crawler's logger
* `-i` if supplied, then triggers an incremental crawl (ie: full = false)
