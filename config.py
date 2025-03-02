import os

from dotenv import load_dotenv

# Load .env file
load_dotenv()

# TODO: add handling when env is not defined
BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")
BITBUCKET_PASSWORD = os.getenv("BITBUCKET_PASSWORD")
BITBUCKET_USERNAME_EMAIL = os.getenv("BITBUCKET_USERNAME_EMAIL")
BITBUCKET_WORKSPACE = os.getenv("BITBUCKET_WORKSPACE")

BASE_API_URL = "https://api.bitbucket.org/2.0"
BITBUCKET_UI_URL = "https://bitbucket.org"
