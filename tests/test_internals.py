import unittest

from tornado import httputil
import mock

import divak.internals


class EnsureRequestIdTransformerTests(unittest.TestCase):

    def test_that_request_id_attribute_created(self):
        request = httputil.HTTPServerRequest(uri='http://google.com/')

        divak.internals.EnsureRequestIdTransformer(request)
        self.assertIs(hasattr(request, 'divak_request_id'), True)

    def test_that_request_id_is_retained_if_present(self):
        request = httputil.HTTPServerRequest(uri='http://google.com/')
        setattr(request, 'divak_request_id', mock.sentinel.some_id)

        divak.internals.EnsureRequestIdTransformer(request)
        self.assertIs(request.divak_request_id, mock.sentinel.some_id)
