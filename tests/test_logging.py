import logging
import unittest

from tornado import testing, web
import divak.api
import divak.internals
import tests.application


class ApiLoggerTests(testing.AsyncHTTPTestCase):

    class HandlerWithLogger(divak.api.Logger, web.RequestHandler):

        def initialize(self):
            self.logger = logging.getLogger('my.custom.logger')
            super(ApiLoggerTests.HandlerWithLogger, self).initialize()

    def setUp(self):
        self.log_manager = logging.root.manager
        self.app = None
        self.log_manager.loggerDict.clear()
        super(ApiLoggerTests, self).setUp()

    def get_app(self):
        self.app = tests.application.Application(
            [web.url('/nologger', divak.api.Logger),
             web.url('/logger', ApiLoggerTests.HandlerWithLogger)])
        return self.app

    def test_that_logger_is_created_if_missing(self):
        logger_name = 'divak.api.Logger'
        self.assertNotIn(logger_name, self.log_manager.loggerDict)
        self.fetch('/nologger')
        self.assertIn(logger_name, self.log_manager.loggerDict)

    def test_that_logger_is_retained_if_set(self):
        self.assertNotIn('my.custom.logger', self.log_manager.loggerDict)
        self.fetch('/logger')
        self.assertIn('my.custom.logger', self.log_manager.loggerDict)


class LogInitializationTests(unittest.TestCase):

    def setUp(self):
        super(LogInitializationTests, self).setUp()
        logging.setLoggerClass(logging.Logger)
        manager = logging.Logger.manager  # type: logging.Manager
        manager.loggerDict.clear()
        for handler in logging.root.handlers:
            filters = []
            for filter in handler.filters:
                if not isinstance(filter,
                                  divak.internals.DivakRequestIdFilter):
                    filters.append(filter)
            handler.filters[:] = filters[:]

    def test_that_new_logger_class_is_inserted(self):
        divak.internals.initialize_logging()
        self.assertIsNot(logging.getLoggerClass(), logging.Logger)
        self.assertTrue(issubclass(logging.getLoggerClass(), logging.Logger))

    def test_that_existing_loggers_are_filtered(self):
        # Install a logger before calling initialize_logging.  Having
        # multiple parts in the name path ensures that the logging layer
        # inserts place holder loggers that we need to account for during
        # initialization.
        logger = logging.getLogger('package.sub.name')
        self.assertIs(logger.__class__, logging.Logger)
        self.assertFalse(
            logger_has_filter(logger, divak.internals.DivakRequestIdFilter))

        divak.internals.initialize_logging()
        self.assertTrue(
            logger_has_filter(logger, divak.internals.DivakRequestIdFilter))

    def test_that_filters_are_not_duplicated(self):
        # verify that a filter is only added to each handler once
        handler = logging.NullHandler()
        handler.addFilter(logging.Filter())  # tests coverage
        logging.getLogger('one').addHandler(handler)
        logging.getLogger('two').addHandler(handler)
        logging.getLogger().addHandler(handler)

        divak.internals.initialize_logging()
        handlers = set()
        for logger in logging.Logger.manager.loggerDict.values():
            if hasattr(logger, 'handlers'):
                handlers.update(logger.handlers)
        for handler in handlers:
            filter_count = 0
            for filter in handler.filters:
                if isinstance(filter, divak.internals.DivakRequestIdFilter):
                    filter_count += 1
            self.assertEqual(filter_count, 1)

    def test_that_calling_initialize_logging_is_idempotent(self):
        divak.internals.initialize_logging()
        divak.internals.initialize_logging()
        for handler in logging.getLogger().handlers:
            count = 0
            for filter in handler.filters:
                if isinstance(filter, divak.internals.DivakRequestIdFilter):
                    count += 1
            self.assertEqual(count, 1)


def logger_has_filter(logger, filter_class):
    """
    Will `logger` execute a filter of `filter_class`?

    :param logging.Logger logger: the logger to examine
    :param class filter_class: the filter class to search for
    :return: :data:`True` if the `logger` contains a `filter_class`
        filter instance in it's chain
    :rtype: bool

    """
    if isinstance(logger, logging.Logger):
        for filter in logger.filters:
            if isinstance(filter, filter_class):
                return True
        for handler in logger.handlers:
            for filter in handler.filters:
                if isinstance(filter, filter_class):
                    return True
        if logger.propagate and logger.parent:
            if logger_has_filter(logger.parent, filter_class):
                return True
    return False
