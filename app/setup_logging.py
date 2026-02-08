import logging
import queue
from logging import handlers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from logging.handlers import QueueListener


def setup_logging() -> QueueListener:
    log_queue = queue.Queue()
    queue_handler = handlers.QueueHandler(log_queue)

    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    handler.setFormatter(formatter)

    listener = handlers.QueueListener(
        log_queue,
        handler,
        respect_handler_level=True,
    )

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(queue_handler)

    listener.start()
    return listener
