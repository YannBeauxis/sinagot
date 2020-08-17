# coding=utf-8

import sys
import logging
from sinagot.utils import (
    record_log_file_path,
    LOG_ORIGIN,
    LOG_RECORD_ID,
    LOG_STEP_LABEL,
)


LOG_FORMAT_UNIT = "%(asctime)s | %({})s : %(message)s".format(LOG_STEP_LABEL)

LOG_FORMAT = "%(asctime)s | %(task)s-%(modality)s-%({})s : %(message)s".format(
    LOG_STEP_LABEL
)


def logger_factory(config, is_unit=False):
    """Create logger with config info"""

    if "log" in config:
        config = config["log"]
    else:
        config = {
            "name": "sinagot",
            "format": "%(asctime)s : %(message)s",
            "level": "INFO",
        }

    logger = logging.getLogger(config["name"])

    handlers = list(logger.handlers)
    for hdlr in handlers:
        logger.removeHandler(hdlr)

    handler = logging.StreamHandler(sys.stdout)
    if "format" in config:
        formatter = logging.Formatter(config["format"])
        handler.setFormatter(formatter)
    handler.addFilter(filter_no_script)
    logger.addHandler(handler)
    if "level" in config:
        logger.setLevel(config["level"])
    logger.debug("log initialized")

    script_handler = logging.StreamHandler(sys.stdout)
    if is_unit:
        log_format = LOG_FORMAT_UNIT
    else:
        log_format = LOG_FORMAT
    script_handler.setFormatter(
        logging.Formatter("%({})s | ".format(LOG_RECORD_ID) + log_format)
    )
    script_handler.addFilter(filter_is_script)
    logger.addHandler(script_handler)

    return logger


def filter_no_script(record):
    try:
        return record.__dict__[LOG_ORIGIN] != "script"
    except KeyError:
        return True


def filter_is_script(record):
    try:
        return record.__dict__[LOG_ORIGIN] == "script"
    except KeyError:
        return False
