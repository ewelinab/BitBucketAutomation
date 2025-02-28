import requests
import pytest
import logging
from config import BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, BITBUCKET_WORKSPACE, BASE_URL


logger = logging.getLogger(__name__)

AUTH = (BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)

REPO_NAME = "test_repo_1"


### 1. CREATE A REPOSITORY ###
def test_create_repository():
    url = f"{BASE_URL}/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}"

    # we do not define project so it will be assigned to last used one
    payload = {
        "scm": "git",
        "is_private": True
    }

    logger.info(f"Creating repository using url: {url}")
    response = requests.post(url, json=payload, auth=AUTH)
    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code in [200, 201], f"Failed to create repo: {response.text}"
    assert response.json().get("name") == REPO_NAME


### 2. LIST & VALIDATE REPOSITORY ###
def test_list_repository():
    url = f"{BASE_URL}/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}"

    logger.info(f"Fetching repository details: {REPO_NAME}")
    response = requests.get(url, auth=AUTH)

    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == 200, f"Failed to list repo: {response.text}"

### 3. CREATE BRANCH AND COMMIT ###

### ✅ Step 1: Check if "main" exists ###
def get_main_branch():
    logger.info("Checking if 'main' branch exists...")

    url = f"{BASE_URL}/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}/refs/branches/main"
    logger.debug(f"GET Request URL: {url}")

    response = requests.get(url, auth=AUTH)

    logger.info(f"Response Status: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    if response.status_code == 200:
        logger.info("✅ 'main' branch already exists.")
        return True
    elif response.status_code == 404:
        logger.warning("⚠️ 'main' branch does not exist. Needs initialization.")
        return False
    else:
        logger.error(f"❌ Unexpected error checking 'main' branch: {response.text}")
        pytest.fail(f"❌ Unexpected error checking 'main' branch: {response.text}")


### ✅ Step 2: Create an Initial Commit to Initialize "main" ###
def initialize_main_branch():
    logger.info("Initializing 'main' branch with an initial commit...")

    url = f"{BASE_URL}/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}/src"
    payload = {
        "message": "Initial commit to create main",
        "branch": "main"
    }
    files = {'README.md': ('README.md', b'# Initial Commit\n')}

    logger.debug(f"POST Request URL: {url}")
    logger.debug(f"Payload: {payload}")

    response = requests.post(url, auth=AUTH, data=payload, files=files)

    logger.info(f"Response Status: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    if response.status_code == 201:
        logger.info("✅ Successfully initialized 'main' branch with initial commit.")
    else:
        logger.error(f"❌ Failed to initialize 'main' branch: {response.text}")
        pytest.fail(f"❌ Failed to initialize 'main' branch: {response.text}")


### ✅ Step 3: Create a New Branch ###
def test_create_branch():
    logger.info(f"Creating a new branch from 'main' in the repository: {REPO_NAME}...")

    if not get_main_branch():
        initialize_main_branch()  # If main does not exist, create it

    branch_name = "test-branch"
    url = f"{BASE_URL}/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}/refs/branches"
    payload = {"name": branch_name, "target": {"hash": "main"}}

    logger.debug(f"POST Request URL: {url}")
    logger.debug(f"Payload: {payload}")

    response = requests.post(url, json=payload, auth=AUTH)

    logger.info(f"Response Status: {response.status_code}")
    logger.debug(f"Response Body: {response.text}")

    if response.status_code == 201:
        logger.info(f"✅ Successfully created the '{branch_name}' branch from 'main'.")
    else:
        logger.error(f"❌ Failed to create branch '{branch_name}': {response.text}")
        pytest.fail(f"❌ Failed to create branch: {response.text}")


### 4. DELETE REPOSITORY ###
def test_delete_repository():
    url = f"{BASE_URL}/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}"

    logger.info(f"Deleting repository: {REPO_NAME}")
    response = requests.delete(url, auth=AUTH)

    logger.info(f"Response: {response.status_code} - {response.text}")

    assert response.status_code == 204, f"Failed to delete repo: {response.text}"

    # Validate deletion
    response = requests.get(url, auth=AUTH)
    assert response.status_code == 404, f"Repository still exists after delete: {response.text}"