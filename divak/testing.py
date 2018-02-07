import logging


class RecordingLogHandler(logging.Handler):
    """
    Log handler that keeps track of log records.

    Install an instance of this class as a handler on a
    :class:`logging.Logger` to keep track of messages that are
    logged.

    .. attribute:: records

       :class:`list` of :class:`logging.LogRecord` instances for
       messages that were logged.

    """

    def __init__(self, *args, **kwargs):
        super(RecordingLogHandler, self).__init__(*args, **kwargs)
        self.records = []

    def emit(self, record):
        self.records.append(record)
