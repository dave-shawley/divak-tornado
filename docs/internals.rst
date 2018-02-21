.. :py:currentmodule:: divak.api
.. _implementation_details:

======================
Implementation Details
======================

Request Id Management
=====================
Propagating incoming request details through the system is at the very heart
of any observability attempt.  The simplest case is copying a header from the
request to the response and making the same identifier available in emitted
log messages.  It is a simple concept and has a profound impact on your
ability to trace a message through the internals of a service and through the
entire system.  The implementation is spread throughout a few classes:

- :class:`.RequestIdPropagator` ensures that a named request header is
  stored as a first-class property on the request
- :class:`.HeaderRelayTransformer` then ensures that the property value is
  added as a response header of the same name
- :class:`.Recorder` is a :class:`tornado.web.Application` mix-in that
  installs instances of the :class:`.HeaderRelayTransformer` when your
  application calls :meth:`~.Recorder.add_divak_propagator`
- :class:`.Logger` is a :class:`tornado.web.RequestHandler` mix-in that adds a
  :class:`logging.LoggerAdapter` instance and inserts the request ID property
  from the request into the logging context -- this makes
  ``%(divak_request_id)s`` work in log messages

Simply making the request ID available throughout the application is a bit
more work than one would expect.  The process relies on an under-documented
Tornado feature called *transformers*.  A transformer is a function that is
called immediately after creating the request handler instance.  It is an
injection point that can extract information from an incoming request or even
modify the request object before it is processed.  The transformer function
returns an object instance that is called immediately before sending the
HTTP response line and again on each subsequent outgoing chunk.  The simplest
implementation is a class since the class itself is callable and returns an
instance.  The following class is a simple no-op implementation of a Tornado
transformer.

.. code:: python

   class NoOpTransformer(object):

      def __init__(self, request):
         pass

      def transform_first_chunk(self, status_code, headers, chunk,
                                include_footers):
         return status_code, headers, chunk

      def transform_chunk(self, chunk, include_footers):
         return chunk

The application installs the transformer by calling
:meth:`~tornado.web.Application.add_transform`.  Then it is called on each
request.  The detailed sequence of events during request processing is:

1. The :class:`tornado.web.HTTPServerRequest` instance is created.
2. The HTTP start line and headers are read and stored in the request object
3. the :class:`tornado.web.RequestHandler` sub-class is determined by the
   application routing rules.
4. A new instance of the request handler is instantiated with the request
   instance.  The :meth:`~tornado.web.RequestHandler.initialize` method is
   called at this time.
5. The transformer functions are invoked with the request object.  In the
   simple case, new transformer instances are created.
6. The :meth:`~tornado.web.RequestHandler.prepare` method is called on the
   request handler instance.
7. The request handler's "action method" (e.g., ``get``, ``post``) is invoked.
8. The request is "finished" if necessary.

A few very important details about this sequence of events:

* When the request handler instance is created in step 4, the request has not
  passed through the transform functions so:

   - The request handler cannot rely on any information that is injected by a
     transformer inside of ``initialize``.
   - The request handler has a chance to modify the request instance before it
     is transformed.

* Request handler **SHOULD NOT** call
  :meth:`~tornado.web.RequestHandler.finish` from within ``initialize``.
  Doing so wreaks havoc with any installed transforms because they will be
  created and initialized *after* the request is already finished and are
  never called again.
* Since :meth:`~tornado.web.RequestHandler.prepare` is permitted to be
  asynchronous, transformers need to be per-request instances or completely
  stateless.  If ``prepare`` yields, then there could be parallel active
  requests so the transformed *SHOULD NOT* contain state.

There is a rather glaring omission in the sequence of events.  *When are the
transform methods invoked?*  ``transform_first_chunk`` is called **BEFORE**
the HTTP response line and headers are written so they can influence the
response headers and status code *after the request handler is done with
them*.  ``transform_chunk`` is called for each body chunk from within
:meth:`~tornado.web.RequestHandler.write`.

The extra wrinkle for the :class:`.HeaderRelayTransformer` is that the name of
the header to relay is configurable so we cannot simply let Tornado create
a class instance for us -- we need to get the header name into the transformer.
Instead, :class:`.RequestIdPropagator` implements a factory method that
returns a new :class:`.HeaderRelayTransformer` instance and installs the
factory method as a transformer function.  The :class:`.HeaderRelayTransformer`
instance inserts the *divak_request_id* property from the request into the
response headers if it is set.

Logging
=======
The :class:`.Recorder` mix-in (over :class:`tornado.web.Application`) ensures
that it is safe to refer to the ``%(divak_request_id)s`` in any log formatter.
During initialization, the :class:`.Recorder` instance installs the
:class:`~divak.internals.DivakLogger` class as the "logger class" by calling
:func:`logging.setLoggerClass`.  Future calls to :func:`logging.getLogger`
will return instances of :class:`~divak.internals.DivakLogger` which is a
sub-class of :class:`logging.Logger`.  This makes the request ID available for
logger instances created after the application is initialized but it doesn't
address existing logger instances.

A :class:`~divak.internals.DivakRequestIdFilter` instance is inserted into
existing :class:`logging.Handler` instances so that any existing loggers can
safely refer to the request ID in their messages as well.  This is done during
application initialization after setting the logging class.  Existing loggers
are visited via the :class:`logging.Manager` global instance.  If the assigned
handlers do not have a :class:`~divak.internals.DivakRequestIdFilter`, then
one is added to the filter chain.

That makes it possible to refer to ``%(divak_request_id)s`` in log formats but
it doesn't actually get the value into the log messages.  This is where the
:class:`divak.api.Logger` mix-in comes into play.  It's raison d'êtra is to
add ``self.logger`` to a :class:`~tornado.web.RequestHandler` instance but it
does one other thing for you -- it inserts the
``self.request.divak_request_id`` into the logging context for you.  This is
what makes the request id available in log messages from your request
handlers.

The next place that we want the request ID to show up is in the Tornado access
log lines.  :class:`.Recorder` re-implements
:meth:`tornado.web.Application.log_request` so that it passes the current
request ID into the Tornado logger.  What it does not do is add the request ID
to the log format -- *you are required to do that if you wish*.  See
:ref:`request_logging` for the details.

Implementation Details
======================

DivakLogger
-----------
.. autoclass:: divak.internals.DivakLogger
   :members:

DivakRequestIdFilter
--------------------
.. autoclass:: divak.internals.DivakRequestIdFilter
   :members:

HeaderRelayTransformer
----------------------
.. autoclass:: divak.api.HeaderRelayTransformer
   :members:

initialize_logging
------------------
.. autofunction:: divak.internals.initialize_logging
