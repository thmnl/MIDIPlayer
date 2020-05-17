import logging

my_logger = None


class LogWrapper:
    def __init__(self, logger):
        self.logger = logger

    def info(self, *args, sep=" "):
        self.logger.info(sep.join("{}".format(a) for a in args))

    def debug(self, *args, sep=" "):
        self.logger.debug(sep.join("{}".format(a) for a in args))

    def warning(self, *args, sep=" "):
        self.logger.warning("WARNING : " + sep.join("{}".format(a) for a in args))

    def error(self, *args, sep=" "):
        self.logger.error("ERROR : " + sep.join("{}".format(a) for a in args))

    def critical(self, *args, sep=" "):
        self.logger.critical("CRITICAL : " + sep.join("{}".format(a) for a in args))

    def exception(self, *args, sep=" "):
        self.logger.exception("EXCEPTION : " + sep.join("{}".format(a) for a in args))


def init(
    args, format="%(message)s",
):
    global my_logger
    logging.basicConfig(format=format)
    _my_logger = logging.getLogger("my_logger")
    root = logging.getLogger()
    root.setLevel(logging.ERROR)
    if args.verbose:
        _my_logger.setLevel(logging.DEBUG)
    elif args.quiet:
        _my_logger.setLevel(logging.ERROR)
    else:
        _my_logger.setLevel(logging.INFO)
    my_logger = LogWrapper(_my_logger)
