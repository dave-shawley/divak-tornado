=============
divák-tornado
=============

|Version| |ReadTheDocs| |CI| |Coverage| |CodeClimate|

Helper classes for observing your Tornado-based HTTP code.

+---------------+----------------------------------------------------+
| Source Code   | https://github.com/dave-shawley/divak-tornado      |
+---------------+----------------------------------------------------+
| Download      | https://pypi.org/project/divak-tornado             |
+---------------+----------------------------------------------------+
| Documentation | https://divak-tornado.readthedocs.io               |
+---------------+----------------------------------------------------+
| Issue Tracker | https://github.com/dave-shawley/divak-tornado      |
+---------------+----------------------------------------------------+

Divák implements patterns for observing inter-service communication in
distributed systems from both a client and a server perspective.  The
primary goal is to provide a nice framework for all aspects of
observability:

* measuring time spent during execution
* counting interesting events
* propagating tokens across inter-service communication that
  allow for tracing of messages
* injecting tracing tokens into log messages

In the past I have approached the problem of observing data flows from
the perspective of the individual aspects of logging, metrics recording,
and error reporting.  Divák takes a different approach.  It provides the
tools to include measurements in your code and the ability to propagate
tokens that correlate all parts of a data flow across multiple services.

This particular library implements observation as an application level
observer, a mix-in class that reads tokens from incoming HTTP requests,
a wrapper that propagates tokens to other services when you make HTTP
requests, and other similar helpers.  The goal is to make it possible
to easily instrument your application code in such a way that operational
metrics are recorded, correlation identifiers are created and propagated
between services, and the same identifiers are included in log messages.
All of this using a single context-manager based instrumentation
mechanism.

Here's an example of the API that I am aiming for,  The request handler uses
two new mix-in classes: ``divak.api.RequestTracker`` and ``divak.api.Logger``.
The request tracker adds methods that implement operation tracing and the
logger is essentially a ``logging.LoggingAdapter`` that injects the
correlation identifiers into ``LogRecord`` instances.  I also used the
``divak.api.HttpClientMixin`` which adds a method to send HTTP requests to
other services that propagates the active span information.

The application also uses two mix-in classes: ``divak.api.Recorder`` and
``divak.api.ProbabilisticSampler``.  The record is responsible for submitting
trace data out-of-band to whatever aggregators you add and the sampler is what
determines how frequently to sample requests.

.. code-block:: python

   from tornado import gen, web
   import divak.api

   class MyHandler(divak.api.RequestTracker, divak.api.Logger,
                   divak.api.HttpClientMixin, web.RequestHandler):
      def initialize(self):
         super(self, MyHandler).initialize()
         self.set_divak_name('foo')
      
      @gen.coroutine
      def get(self):
         with self.record_operation('query-db'):
            rows = yield self.query('...')
            self.add_divak_tag('query-db.rowcount', len(rows))

         output = []
         for row in rows:
            self.logger.debug('requesting %r', row['id'])
            response = yield self.send_request(
               'http://.../?id={}'.format(row['id']),
               method='GET')
            output.append(response.body)
         self.set_status(200)
         self.send_response(output)

   class Application(divak.api.Recorder, divak.api.ProbabilisticSampler,
                     web.Application):
      
      def __init__(self, *args, **kwargs):
         handlers = [web.url(r'/', MyHandler)]

         super(Application, self).__init__(handlers, *args, **kwargs)
         self.set_divak_service('my-service')
         self.set_divak_sample_probability(1.0 / 1000.0)
         self.add_divak_reporter(
            divak.api.ZipkinReporter('http://127.0.0.1:9411/api/v2'))

This example will result in `zipkin`_ tracing for ``GET /`` requests which
record spans for the database query and each HTTP API call.

Related Work
------------
* `sprockets.http`_ - implements helpers that run Tornado HTTP applications
  and configure logging to facilitate tracing
* `sprockets.mixins.correlation`_ - creates a correlation ID that can be
  passed from service to service using HTTP headers
* `sprockets.mixins.metrics`_ - implements recording of runtime metrics using
  either statsd or InfluxDB
* `sprockets.mixins.sentry`_ - implements error reporting to `sentry`_ for
  unhandled exceptions
* `sprockets.mixins.statsd`_ - implements recording of runtime metrics using
  statsd
* `sprockets-influxdb`_ - implements recording of runtime measurements using
  InfluxDB as a back end

.. |CI| image:: https://img.shields.io/circleci/project/github
   /dave-shawley/divak-tornado.svg
   :target: https://circleci.com/gh/dave-shawley/divak-tornado
.. |CodeClimate| image:: https://codeclimate.com/github/dave-shawley
   /divak-tornado/badges/gpa.svg
   :target: https://codeclimate.com/github/dave-shawley/divak-tornado
.. |Coverage| image:: https://img.shields.io/codecov/c/github/dave-shawley
   /divak-tornado.svg
   :target: https://codecov.io/gh/dave-shawley/divak-tornado
.. |ReadTheDocs| image:: https://readthedocs.org/projects/divak-tornado
   /badge/?version=stable
   :target: https://divak-tornado.readthedocs.io/
.. |Version| image:: https://badge.fury.io/py/divak-tornado.svg
   :target: https://pypi.org/project/divak-tornado

.. _sentry: https://sentry.io/
.. _sprockets.http: https://github.com/sprockets/sprockets.http
.. _sprockets.mixins.correlation: https://github.com/sprockets
   /sprockets.mixins.correlation
.. _sprockets.mixins.metrics: https://github.com/sprockets
   /sprockets.mixins.metrics
.. _sprockets.mixins.sentry: https://github.com/sprockets
   /sprockets.mixins.sentry
.. _sprockets.mixins.statsd: https://github.com/sprockets
   /sprockets.mixins.statsd
.. _sprockets-influxdb: https://github.com/sprockets/sprockets-influxdb
.. _zipkin: https://zipkin.io
