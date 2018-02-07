class DivakTagged(object):

    def add_divak_tag(self, name, value):
        pass


class IdentityTransformer(object):
    """Minimal tornado transform implementation."""

    def __init__(self, request, *args, **kwargs):
        pass

    def transform_first_chunk(self, status_code, headers, chunk,
                              include_footers):
        return status_code, headers, chunk

    def transform_chunk(self, chunk, include_footers):
        return chunk


class EnsureRequestIdTransformer(IdentityTransformer):
    """
    Transformer that creates the ``divak_request_id`` property on requests.

    This simple Tornado transformer uses :func:`setattr` to ensure that
    every request has a ``divak_request_id`` property.

    """

    def __init__(self, request, *args, **kwargs):
        if not hasattr(request, 'divak_request_id'):
            setattr(request, 'divak_request_id', None)
        super(EnsureRequestIdTransformer, self).__init__(
            request, *args, **kwargs)
