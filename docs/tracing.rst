.. :py:currentmodule:: divak.api

Request Tracing
===============

Correlation Headers
-------------------
.. index:: RequestIdPropagator
.. index:: HTTP Header;Request-ID

The simplest form of tracing a request is to pass a header with a correlation
ID through the system.  The :class:`.RequestIdPropagator` class simply
propagates a named header from the request into the response.  The default
behavior is to relay a request header named ``Request-ID`` from request to
response.  This functionality is enabled by adding
a :class:`.RequestIdPropagator` instance to your application by calling
:meth:`~.Recorder.add_divak_propagator` as shown below.

.. literalinclude:: ../examples/request_tracing.py
   :pyobject: MyApplication
   :caption: examples/request_tracing.py

This simple change will copy the ``Request-ID`` header from the request
headers to the response headers.  Having a HTTP header that is relayed
from request to response makes it possible to trace the processing of
a request through multiple services provided that you record it somewhere.

.. code-block:: http
   :caption: Request with header
   :emphasize-lines: 6

   GET /status HTTP/1.1
   Accept: */*
   Accept-Encoding: gzip, deflate
   Connection: keep-alive
   Host: 127.0.0.1:8000
   Request-ID: a6bd045cdcf64451a076a59bdb367ba6
   User-Agent: HTTPie/0.9.9

.. code-block:: http
   :caption: Response with copied header
   :emphasize-lines: 6

   HTTP/1.1 200 OK
   Content-Length: 61
   Content-Type: application/json
   Date: Sat, 10 Feb 2018 13:48:41 GMT
   Etag: "e3c1480268930c91ab9eb759a1fa5fcad3ab5e28"
   Request-Id: a6bd045cdcf64451a076a59bdb367ba6
   Server: TornadoServer/4.5.3

   {
      "service": "my-service",
      "status": "ok",
      "version": "0.0.0"
   }

If the header is not included in the request, then it will generate a UUIDv4
value and insert it into the response.  Of course, the value generation
function can be overridden to anything you want by passing the
``value_factory`` keyword to :class:`.RequestIdPropagator`.

.. code-block:: http
   :caption: Request without header

   GET /status HTTP/1.1
   Accept: */*
   Accept-Encoding: gzip, deflate
   Connection: keep-alive
   Host: 127.0.0.1:8000
   User-Agent: HTTPie/0.9.9

.. code-block:: http
   :caption: Response with generated header
   :emphasize-lines: 6

   HTTP/1.1 200 OK
   Content-Length: 61
   Content-Type: application/json
   Date: Sat, 10 Feb 2018 13:52:42 GMT
   Etag: "e3c1480268930c91ab9eb759a1fa5fcad3ab5e28"
   Request-Id: 31510218-abb2-49b6-bfd3-a036fe4f6113
   Server: TornadoServer/4.5.3

   {
       "service": "my-service",
       "status": "ok",
       "version": "0.0.0"
   }

Request Logging
---------------
The :class:`divak.api.Recorder` class modifies the Python :mod:`logging`
module to ensure that you can use ``%(divak_request_id)s`` in log formats.
It also overrides the :meth:`~tornado.web.Application.log_request` method and
outputs something closer to a standard access log line using the following log
format::
   
   $REMOTE-IP "$METHOD $URI" $STATUS "$USER-AGENT" $PROCESSING-TIME

For example::

   127.0.0.1 "GET /status" 200 "curl/7.54.0" 0.001341104507446289

The ``$PROCESSING-TIME`` is in decimal seconds and the user-agent & request id
portions both default to ``"-"`` if they are missing for some reason.  You can
modify this behavior by overriding the method in your application class or by
adding a custom formatting pattern to ``tornado.log.access_log``.  The
following dictionary is passed as the ``extra`` parameter to the log method:

.. code-block:: python

   extra = {
      'remoteip': '127.0.0.1',
      'status': handler.get_status(),
      'elapsed': request.request_time(),
      'method': request.method,
      'uri': request.uri,
      'useragent': request.headers.get('User-Agent', '-'),
      'divak_request_id': getattr(request, 'divak_request_id', '-'),
   }
