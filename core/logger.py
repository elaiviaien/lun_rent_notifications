import logging
import os

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
script_dir = os.path.dirname(os.path.abspath(__file__))

log_file_path = os.path.join(script_dir, "../scraping.log")

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

fh = logging.FileHandler(log_file_path)
fh.setFormatter(formatter)

logger.addHandler(fh)