===============
Request Tracing
===============

Application Requirements
========================
Your application needs to inherit from :class:`divak.api.Recorder` to use
divák.  The ``Recorder`` class provides methods to inject observers into the
request processing pipeline.  It is a strictly *opt-in* interface in that you
must explicitly add observers to get any functionality.  By default, the
``Recorder`` class provides no functionality.

Correlation Headers
===================
The simplest form of tracing a request is to pass a header with a correlation
ID through the system.  The :class:`divak.api.RequestIdPropagator` class
simply propagates a named header from the request into the response.  The
default behavior is to relay a request header named ``Request-ID`` from
request to response.  It will generate a new UUIDv4 value and insert it into
the response headers if the request does not include a ``Request-ID``.

This functionality is enabled by adding a ``RequestIdPropagator`` instance to
your application by calling :meth:`~divak.api.Recorder.add_divak_propagator`
as shown below.  You can customize the propagator before adding it to your
application if you want to change the name of the header or use a different
default value factory.

.. code-block:: python

   from tornado import web
   import divak.api

   class MyApplication(divak.api.Recorder, web.Application):

      def __init__(self, *args, **kwargs):
         handlers = [
            # your handlers here
         ]
         super(MyApplication, self).__init__(handlers, *args, **kwargs)
         self.set_divak_service('my-service')
         self.add_divak_propagation(divak.api.RequestIdPropagator())
