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

    fmt_prefix = "[" + GRAY + "%(asctime)s" + RESET + "]"
    fmt_date = "%H:%M:%S"

    FORMATS = {
        logging.INFO: fmt_prefix + " " + WHITE + "INFO" + RESET + ": %(message)s",
        logging.DEBUG: fmt_prefix + " " + BLUE + "DEBUG" + RESET + ": %(message)s",
        logging.WARNING: fmt_prefix + " " + YELLOW + "WARNING" + RESET + ": %(message)s",
        logging.ERROR: fmt_prefix + " " + RED + "ERROR" + RESET + ": %(message)s",
        logging.CRITICAL: fmt_prefix + " " + RED + "CRITICAL" + RESET + ": %(message)s",
    }

    def format(self, record):
        formatter = logging.Formatter(self.FORMATS.get(record.levelno), self.fmt_date)
        return formatter.format(record)


def _create_logger() -> logging.Logger:
    logger = logging.getLogger("slash")
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(Formatter())
    logger.addHandler(ch)
    return logger


LOGGER = _create_logger()
