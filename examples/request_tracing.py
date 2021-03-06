import json
import logging

from tornado import ioloop, web
import divak.api


class StatusHandler(divak.api.Logger, web.RequestHandler):

    def get(self):
        self.logger.info('processing get request')
        self.set_status(200)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps({'service': 'my-service',
                               'version': '0.0.0',
                               'status': 'ok'}).encode('utf-8'))


class MyApplication(divak.api.Recorder, web.Application):

    def __init__(self, *args, **kwargs):
        super(MyApplication, self).__init__(
            [web.url('/status', StatusHandler)],
            *args, **kwargs)
        self.set_divak_service('my-service')
        self.add_divak_propagator(divak.api.RequestIdPropagator())


def main():
    logging.basicConfig(
        level=logging.INFO,
        format=('%(levelname)1.1s - %(name)s: %(message)s '
                '{%(divak_request_id)s}'))
    app = MyApplication(debug=True)
    app.listen(8000)
    ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
