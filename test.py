import json
import logging

log_format = (
    "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(lineno)d::  %(message)s"
)
logger: logging.Logger = logging.getLogger(__name__)
logging.basicConfig(level=0, format=log_format)
# NOTSET	0
# DEBUG	10
# INFO	20
# WARNING	30
# ERROR	40
# CRITICAL/FATAL	50

logger.debug("Debug message")

logger.info("Informative message")

logger.error("Error message")

logger.critical("Error message")

var_1 = [[[0.1, 0.2], "hidden"], [[0.1, 0.2], "open"]]
print(type(var_1))
print(n := json.dumps(var_1), type(n))
print(j := json.loads(n), type(j))
