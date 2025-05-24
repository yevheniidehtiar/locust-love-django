import logging
import sys

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])

logger = logging.getLogger("startup_logger")

logger.debug("This is a DEBUG message from startup_logger.py")
logger.info("This is an INFO message from startup_logger.py")
logger.warning("This is a WARNING message from startup_logger.py")
logger.error("This is an ERROR message from startup_logger.py")

print("Direct print to stdout from startup_logger.py")