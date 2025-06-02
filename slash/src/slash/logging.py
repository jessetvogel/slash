import logging


class Formatter(logging.Formatter):
    GRAY = "\x1b[90m"
    RED = "\x1b[31m"
    GREEN = "\x1b[32m"
    YELLOW = "\x1b[33m"
    BLUE = "\x1b[34m"
    WHITE = "\x1b[37m"
    BOLD = "\x1b[1m"
    RESET = "\x1b[0m"
    format_str = (
        "["
        + BLUE
        + "%(name)s"
        + RESET
        + "]["
        + GRAY
        + "%(levelname)s"
        + RESET
        + "] "
        + "%(message)s"
    )

    FORMATS = {
        logging.DEBUG: format_str,
        logging.INFO: format_str,
        logging.WARNING: format_str,
        logging.ERROR: format_str,
        logging.CRITICAL: format_str,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger: logging.Logger | None = None


def create_logger() -> logging.Logger:
    global logger
    if logger is None:
        logger = logging.getLogger("slash")
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(Formatter())
        logger.addHandler(ch)
    return logger
