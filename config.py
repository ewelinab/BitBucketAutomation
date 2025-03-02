import logging
import os
import sys

import pytest
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load .env file
load_dotenv()

# TODO: add handling when env is not defined
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")
BITBUCKET_PASSWORD = os.getenv("BITBUCKET_PASSWORD")
BITBUCKET_USERNAME_EMAIL = os.getenv("BITBUCKET_USERNAME_EMAIL")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

if not BITBUCKET_USERNAME:
    logger.error("Environment variable BITBUCKET_USERNAME is not defined or is empty.")
if not BITBUCKET_APP_PASSWORD:
    logger.error("Environment variable BITBUCKET_APP_PASSWORD is not defined or is empty.")
if not BITBUCKET_PASSWORD:
    logger.error("Environment variable BITBUCKET_PASSWORD is not defined or is empty.")
if not BITBUCKET_USERNAME_EMAIL:
    logger.error("Environment variable BITBUCKET_USERNAME_EMAIL is not defined or is empty.")
if not BITBUCKET_WORKSPACE:
    logger.error("Environment variable BITBUCKET_WORKSPACE is not defined or is empty.")

# If all required variables are set, log success
if all([BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, BITBUCKET_PASSWORD, BITBUCKET_USERNAME_EMAIL, BITBUCKET_WORKSPACE]):
    logger.info("All environment variables are set up correctly.")
else:
    logger.info("Not all environment variables are set up correctly.")
    sys.exit(1)

BASE_API_URL = "https://api.bitbucket.org/2.0"
BITBUCKET_UI_URL = "https://bitbucket.org"
