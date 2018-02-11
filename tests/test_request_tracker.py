import logging
import uuid

from tornado import testing

import divak.api
import divak.testing
import tests.application


class RequestIdPropagationTests(testing.AsyncHTTPTestCase):

    def get_app(self):
        self._app = tests.application.Application()
        self._app.add_divak_propagator(divak.api.RequestIdPropagator())
        return self._app

    def setUp(self):
        self._app = None
        super(RequestIdPropagationTests, self).setUp()

    def test_that_request_id_header_is_generated(self):
        response = self.fetch('/trace')
        self.assertIsNotNone(response.headers.get('Request-Id'))

    def test_that_request_id_header_is_copied(self):
        request_id = 'whatever'
        response = self.fetch('/trace', headers={'Request-Id': request_id})
        self.assertEqual(response.headers['request-id'], request_id)

    def test_that_response_header_generation_can_be_disabled(self):
        self._app.transforms = [
            t for t in self._app.transforms
            if not isinstance(t, divak.api.HeaderRelayTransformer)]
        self._app.add_divak_propagator(
            divak.api.RequestIdPropagator(value_factory=None))
        response = self.fetch('/trace')
        self.assertIsNone(response.headers.get('Request-Id'))

    def test_that_response_header_is_generated_on_failure(self):
        response = self.fetch('/trace?status=500&raise')
        self.assertEqual(response.code, 500)
        self.assertIsNotNone(response.headers.get('Request-Id'))

    def test_that_log_messages_have_request_ids(self):
        recorder = divak.testing.RecordingLogHandler()
        logger = logging.getLogger('tests.application.TracedHandler')
        logger.addHandler(recorder)

        request_id = str(uuid.uuid4())
        self.fetch('/trace', headers={'Request-Id': request_id})
        self.assertGreater(len(recorder.records), 0)
        for record in recorder.records:
            self.assertEqual(record.divak_request_id, request_id)
