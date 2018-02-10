from tornado import web

from divak import api


class TracedHandler(api.RequestTracker, api.Logger, web.RequestHandler):

    def get(self):
        status_code = int(self.get_query_argument('status', '200'))
        should_raise = self.get_query_argument('raise', None)
        self.logger.debug('processing GET status=%d raise=%r',
                          status_code, should_raise)

        if should_raise is not None:
            raise web.HTTPError(status_code)

        self.set_status(status_code)

        # this is the only good way to fully exercise the tornado
        # response processing stack
        self.write('chunk one\n')
        self.flush()
        self.finish('chunk two\n')


class Application(api.Recorder, api.AlwaysSampleSampler,
                  web.Application):

    def __init__(self, handlers=None, *args, **kwargs):
        if handlers is not None:
            handlers.append(web.url('/trace', TracedHandler))
        else:
            handlers = [web.url('/trace', TracedHandler)]
        super(Application, self).__init__(handlers, *args, **kwargs)
        self.set_divak_service('test-application')
