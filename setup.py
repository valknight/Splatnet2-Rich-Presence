import os
import sys
import time
from shutil import copyfile, rmtree
from config.logger import logger

quiet = True  # set this to false if you're having issues installing to debug stuff

if quiet:
    quiet = "-q"
else:
    quiet = ""

logger.info("Installing requirements...")
response = os.system(
    '{} -m pip install -r requirements.txt {}'.format(sys.executable, quiet))
if response != 0:
    logger.error(
        "Failed to instal system wide (we recommend a venv if you're not!")
    logger.info("Attempting to install as a user package")
    response = os.system(
        '{} -m pip install -r requirements.txt {} --user'.format(sys.executable, quiet))

if response == 0:
    logger.info("Requirements installed! Go have some fun!")
    sys.exit(0)
else:
    logger.info(
        "Something went wrong while installing requirements. Check your python setup and permissions.")
    sys.exit(1)
