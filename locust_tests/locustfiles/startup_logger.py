import logging
import sys
# from http.client import HTTPConnection

# Configure logging
logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)
# HTTPConnection.debuglevel = 0
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True

logger.debug("This is a DEBUG message from startup_logger.py")
logger.info("This is an INFO message from startup_logger.py")
logger.warning("This is a WARNING message from startup_logger.py")
logger.error("This is an ERROR message from startup_logger.py")

print("Direct print to stdout from startup_logger.py")
