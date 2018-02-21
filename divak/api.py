import logging
import uuid

from tornado import gen, web
import tornado.log

import divak.internals


class Recorder(web.Application):
    """Imbues an application with recording abilities."""

    def __init__(self, *args, **kwargs):
        super(Recorder, self).__init__(*args, **kwargs)
        self.add_transform(divak.internals.EnsureRequestIdTransformer)
        divak.internals.initialize_logging()

    def set_divak_service(self, service_name):
        """
        Set the name of the service for reporting purposes.

        :param str service_name: name to use when reporting to an
            observer

        """

    def add_divak_propagator(self, propagator):
        """
        Add a propagation instance that inspects each request.

        :param propagator: a propagator instance to inspect requests
            and potentially modify responses

        """
        propagator.install(self)

    def add_divak_reporter(self, reporter):
        """
        Add a reporter instance.

        :param reporter: a reporter instance to receive observations

        """

    def log_request(self, handler):
        """
        Override ``log_request`` to improve logging format.

        :param tornado.web.RequestHandler handler: the handler that
            processed the request

        """
        if handler.get_status() < 400:
            log_method = tornado.log.access_log.info
        elif handler.get_status() < 500:
            log_method = tornado.log.access_log.warning
        else:
            log_method = tornado.log.access_log.error

        request = handler.request  # type: tornado.httpserver.HTTPRequest
        args = {'remoteip': '127.0.0.1',
                'status': handler.get_status(),
                'elapsed': request.request_time(),
                'method': request.method,
                'uri': request.uri,
                'useragent': request.headers.get('User-Agent', '-'),
                'divak_request_id': getattr(request, 'divak_request_id', '-')}
        log_method(
            '{remoteip} "{method} {uri}" {status} "{useragent}" '
            '{elapsed:.6f}'.format(**args), extra=args)


class RequestIdPropagator(object):
    """
    Propagates Request-IDs between services.

    :param str header_name: the name of the request header to propagate.
        If this value is unspecified, then the header name defaults to
        ``Request-ID``.
    :keyword value_factory: if this keyword is specified, then it's value
        is called to generate a response header if a new header value is
        required.  If this value is unspecified, then a UUID4 will be
        generated.

    This class implements propagation of a request header into the
    response.  If the incoming request does not include a matching header,
    then a new value will be generated by calling `value_factory`.  You
    can disable the generation of new values by setting `value_factory`
    to :data:`None`.

    """

    def __init__(self, header_name='Request-Id', *args, **kwargs):
        super(RequestIdPropagator, self).__init__()
        self._header_name = header_name
        self._value_factory = kwargs.get('value_factory', uuid.uuid4)

    def install(self, application):
        """
        Install the propagator into the application.

        :param tornado.web.Application application: the application
            to install this propagator into
        :returns: :data:`True` if the propagator wants to be called
            in the future or :data:`False` otherwise
        :rtype: bool

        """
        application.add_transform(HeaderRelayTransformer(self._header_name,
                                                         self._value_factory))
        return False


class HeaderRelayTransformer(object):
    """
    Tornado transformer that relays a header from request to response.

    :param str header_name: the name of the header to relay from
        request to response
    :param value_factory: callable that generates a new value

    Setting `value_factory` to :data:`None` disables the generation
    of response header values when the header is missing from the
    request.

    This class implements the under-documented Tornado transform
    interface.  Transforms are called when the application starts
    processing a request.  The ``__call__`` method can return a
    object that is used to process outgoing chunks.  This class
    implements :meth:`.__call__` to return ``self`` so that the
    :meth:`transform_first_chunk` and :meth:`transform_chunk`
    methods are called to process outgoing data.

    """

    def __init__(self, header_name, value_factory):
        super(HeaderRelayTransformer, self).__init__()
        self._header_name = header_name
        self._value_factory = value_factory
        self._header_value = None

    def __call__(self, request):
        """
        Start processing `request` and set up future processing.

        :param tornado.httputil.HTTPServerRequest request: the request
            that is being processed
        :return: an instance that defines `transform_first_chunk` and
            `transform_chunk` methods

        This method returns a transformer that will be called to transform
        outgoing body chunks.  In this case, we simply return `self`.  The
        :meth:`.transform_first_chunk` and :meth:`.transform_chunk` methods
        will be called as chunks are written by the request handler.

        """
        self._header_value = request.headers.get(self._header_name, None)
        if self._header_value is None and self._value_factory is not None:
            self._header_value = str(self._value_factory())
        request.divak_request_id = self._header_value
        return self

    def transform_first_chunk(self, status_code, headers, chunk,
                              include_footers):
        """
        Called to process the first chunk.

        :param int status_code: status code that is going to be
            returned in the response
        :param tornado.httputil.HTTPHeaders headers: response headers
        :param chunk: the data chunk to transform
        :param bool include_footers: should footers be included?
        :return: the status code, headers, and chunk to use as a tuple

        This method may inject a response header into `headers`.  The
        remaining parameters are passed through as-is.

        """
        if self._header_value is not None:
            # would like to use setdefault but HTTPHeaders does
            # not support it in tornado 4.3
            if headers.get(self._header_name, None) is None:
                headers[self._header_name] = self._header_value
        return status_code, headers, chunk

    def transform_chunk(self, chunk, include_footers):
        """
        Called to transform subsequent chunks.

        :param chunk: the data chunk to transform
        :param bool include_footers: should footers be included?
        :return: the possibly transformed chunk

        This implementation returns `chunk` as-is.

        """
        return chunk


class Logger(web.RequestHandler):
    """
    Imbues a :class:`tornado.web.RequestHandler` with a contextual logger.

    This class adds a ``logger`` attribute that inserts divak tags into
    the logging record.  Tags added by calling :meth:`.add_divak_tag` are
    automatically made available in log messages.  The ``divak_request_id``
    value is guaranteed to be available in all log messages provided that
    you are using :class:`.Application` in your application's class list.

    The ``logger`` attribute is set in :meth:`.prepare` and will wrap
    an existing ``logger`` attribute or create a new one using the self's
    class module and class name as the logger name.

    .. attribute:: logger

       A :class:`logging.LoggerAdapter` that inserts divak tags into log
       records using the ``extra`` dict.

    """

    def __init__(self, *args, **kwargs):
        self._logging_context = {}
        super(Logger, self).__init__(*args, **kwargs)

    @gen.coroutine
    def prepare(self):
        if hasattr(self, 'logger'):
            logger = self.logger
        else:
            full_name = '{}.{}'.format(self.__class__.__module__,
                                       self.__class__.__name__)
            logger = logging.getLogger(full_name)
        self.logger = logging.LoggerAdapter(logger, self._logging_context)
        self._logging_context['divak_request_id'] = (
            self.request.divak_request_id)

        maybe_future = super(Logger, self).prepare()
        if maybe_future:  # pragma: no cover -- pure paranoia
            yield maybe_future
