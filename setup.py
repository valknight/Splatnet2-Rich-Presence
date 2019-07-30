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

## UPGRADING PIP VERSION (CAUSE PYTHON 3.6.0 CONTAINS A LOWER PIP VERSION)
logger.info("Upgrading PIP to the latest version...")
response = os.system('{} -m pip install --upgrade pip {}'.format(sys.executable, quiet))


if response != 0:
    logger.error("Failed to upgrade PIP to the latest version.")
    sys.exit(1)
else: 
    logger.info("PIP has been upgraded successfully!")

## Installing the packages from the requirements textfile
logger.info("Installing requirements...")
response2 = os.system(
    '{} -m pip install -r requirements.txt {}'.format(sys.executable, quiet))
if response2 != 0:
    logger.error(
        "Failed to instal system wide (we recommend a venv if you're not!")
    logger.info("Attempting to install as a user package")
    response2 = os.system(
        '{} -m pip install -r requirements.txt {} --user'.format(sys.executable, quiet))

if response == 0:
    logger.info("Requirements installed! Go have some fun!")
    sys.exit(0)
else:
    logger.info(
        "Something went wrong while installing requirements. Check your python setup and permissions.")
    sys.exit(1)
