import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BITBUCKET_USERNAME = os.getenv("BITBUCKET_USERNAME")
BITBUCKET_APP_PASSWORD = os.getenv("BITBUCKET_APP_PASSWORD")

BITBUCKET_WORKSPACE = "bbautomate"  # Bitbucket workspace name
BASE_URL = "https://api.bitbucket.org/2.0"