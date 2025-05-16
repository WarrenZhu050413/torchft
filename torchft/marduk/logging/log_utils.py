import logging
from typing import TYPE_CHECKING

def log_and_raise_exception(logger: logging.Logger, msg: str, exc_info: bool = False) -> None:
    logger.exception(msg, exc_info=exc_info)
    raise Exception(msg)