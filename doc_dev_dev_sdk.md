---
title: Docido Crawler SDK
keywords: crawlers, development, sdk
last_updated: November 23, 2015
summary: ""
---

## Card attachments

Docido SDK provides several ways for a pull-crawler to push web resources and binary files. When such content is pushed, then the framework tries to extract additional information the payload may provide like the text it contains, a title, description, ...

There are 3 different content a pull-crawler may push whose analysis is made later on:

* URL to either web page, text, or binary files.
* a blob of bytes with a mime type
* a stream to any resource, useful when HTTP headers are required to access the resource.

### URL

Reference to URL can be specified in a nested document in the `attachments` field. The `type` of the attachment must be **link**. For instance:

```json
{
  "id": "1234",
  "service": "lambda",
  "attachments": [
    {
      "type": "link",
      "url": "http://google.com"
    }
  ]
}
```

For such attachment, Docido will tries to download the webpage and enrich the nested attachment with the page title, description, and text. It also works for links to binary files like PDF, words documents, ...
The MIME type is deduced from the *Content-Type* header specified in the HTTP response. If the pull-crawler already knows it, it should force its value by providing the `mime_type` attribute.

This behavior can be de-clutched with the special `_analysis` attribute set to `False` in the nested document:

```json
{
  "id": "1234",
  "service": "lambda",
  "attachments": [
    {
      "type": "link",
      "_analysis": False,
      "url": "http://skip/analysis/of/this/link"
    }
  ]
}
```


### Blob of bytes

If the pull-crawler has the binary content of the payload to index, it can be specified in the `bytes` attribute of an attachment. The attachment must also provide the `mime_type` attribute so that the framework can use the most appropriate content analyzer.
The crawler may provide in the same attachment any information regarding the payload, for instance:


```json
{
  "id": "1234",
  "service": "lambda",
  "attachments": [
    {
      "type": "file",
      "filename": "foo.pdf",
      "mime_type": "application/pdf",
      "bytes": "..."
    }
  ]
}
```

### Stream

This mode allows you to delay download of the payload later to reduce memory contention of your process. The stream must be an instance of `docido_sdk.toolbox.http_ext.delayed_request`.

## Tasks dispatch

Pull-crawler tasks are executed with [Celery](http://www.celeryproject.org/), and Docido SDK provides various methods to control how these tasks are being scheduled:

* *independant sub-tasks*: `Crawler.iter_crawl_tasks` simply returns a list of tasks, executed in parallel.
* *group of sub-tasks*: `Crawler.iter_crawl_tasks` returns a list of list of tasks that can be executed in parallel:
  * Tasks of a given list are executed sequentialy.
  * 2 different list of tasks are executed in parallel.

### Max concurrent tasks per crawl

When a pull-crawler simply provides a list of tasks, Docido's internal framework will split them in sub-lists to control how many tasks are executed in parallel. Default value is set to 10, and can be updated if necessary.

For instance, if the API your crawler fetches accepts no more than 2 connections at the same time, then you can specify override the default `max_concurrent_tasks`  in the `dict`  returned by the `Crawler.iter_crawl_tasks` method and specify 2 instead:

```python
class Crawler(Component):
    def iter_crawl_tasks(...):
       return {
           'tasks': [...],
           'max_concurrent_tasks': 2
       }
```

If you want to set a value greater than the default value (which is 10), please contact Cogniteev's developers and explain your use-case.

### Passing data from a task to another

If you crawler returns a list of tasks sequences, then you can leverage the `prev_result` parameter given to sub-task. It will contain what the previous task returned. Note that the `prev_result` parameter given to the first task of every sequence will be `None`.

### sub-task retry mechanism

There are many use-cases where you want to retry a task later on:

* You cannot contact API
* You reached the API's rate limits.

To do so, a sub-task can raise an instance of `docido_sdk.crawler.Retry` exception class. `Retry` exception accepts a bunch of arguments in constructor to specify when to retry the current task.

### side-effects with `Retry` exception

Furthermore, you can provide the `Retry` class keyword arguments that will be given to the retried task.



Sample below highlights the _retry_ capabilities:

1. During the initial scan, let's assume there are 10 pages to crawl:
  1. `iter_crawl_tasks` asks the `crawl_page` sub-task to be called with:
    * `since=None`
    * `crawl_start=UNIX_TIMESTAMP`, for instance 1447083795
  1. First call to `crawl_page` with `page=1`, will submit cards to Docido index, and ask the `crawl_page` subtask to be called with `page=2`, and so on.
  1. When `page=11`, then the `fetch_page` method raise an `UnknownPage` exception, meaning that the crawl is terminated and it is time to update the crawler checkpoint.
1. When the account synchronization is recalled few hours later, then `since`  is set to the date when the previous crawl began so that `ClientAPI.fetch_page` can only provides changes that occured since then.


```python
import functools
from docido_sdk.core import Core, implements
from docido_sdk.toolbox.date_ext import timestamp_ms


def crawl_page(index, token, prev_result, logger,
               since=None, crawl_start=None, page=1):
    client = ClientApi(token)
    try:
        index.push_cards(to_docido_cards(client.fetch_page(
            page=page,
            since=since)
        ))
    except UnknownPage:
        index.set_kv('since', crawl_start)
    else:
        raise Retry(page=page + 1, countdown=60)


class Crawler(Component):
    implements(ICrawler)
    service_name = 'my_service'

    def iter_crawl_tasks(self, index, *args, **kwargs):
        return {
            'tasks': functools.partial(crawl_page,
                crawl_start=timestamp_ms.now()
                since=index.get_kv('since')
            ),
        }
```


### Common errors

#### Passing huge payload

It is not recommended to use huge objects:

* in parameters specified in the `future` subtasks
* returned by sub-tasks.

You may only store object's identifier, not their content.

#### Dispatch your API calls among different sub-tasks

The `iter_crawl_tasks` method is only meant to enumerate what is to be done by the returned sub-tasks. You may not call the fetched API to retrieve document's content.
