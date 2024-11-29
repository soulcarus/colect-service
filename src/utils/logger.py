import logging
import sys
from logging.handlers import RotatingFileHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'collector.log',
            maxBytes=10000000,
            backupCount=5
        ),
        logging.StreamHandler(sys.stdout)
    ]
)

log = logging.getLogger('collector')