import logging
import unittest.mock

from tornado import httputil, testing, web

import divak.api
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
        self.assertNotIn(divak.api.Logger.__name__,
                         self.log_manager.loggerDict)
        self.fetch('/nologger')
        self.assertIn(divak.api.Logger.__name__, self.log_manager.loggerDict)

    def test_that_logger_is_retained_if_set(self):
        self.assertNotIn('my.custom.logger', self.log_manager.loggerDict)
        self.fetch('/logger')
        self.assertIn('my.custom.logger', self.log_manager.loggerDict)

    def test_that_none_is_not_a_valid_tag(self):
        request = httputil.HTTPServerRequest(uri='http://example.com',
                                             connection=unittest.mock.Mock())
        handler = divak.api.Logger(self.app, request)
        handler.add_divak_tag('tag', 'value')
        handler.add_divak_tag('not-a-tag', None)
        self.assertDictEqual(handler._logging_context, {'tag': 'value'})
