import os

import allure
import pytest
import requests
import logging
import shutil
import time
from git import Repo
from config import BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, BITBUCKET_WORKSPACE

# Setting up the logger for the script
logger = logging.getLogger(__name__)

# Constants for repository names and URLs
REPO_NAME = "git_test_repo"
BITBUCKET_API_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}"
LOCAL_REPO_PATH = ".tmp/git_test_repo"
REPO_URL = f"https://{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}@bitbucket.org/{BITBUCKET_WORKSPACE}/{REPO_NAME}.git"
MODIFIED_FILE = "README.md"


@pytest.fixture(scope="module")
def git_operations_fixture():
    """
    Fixture for git operations
    """
    pass


def clone_repo():
    """
    Clones the repository from Bitbucket into a local directory.
    If the directory already exists, it is removed before cloning.

    Returns:
    Repo: A GitPython Repo object for the cloned repository.
    """
    if os.path.exists(LOCAL_REPO_PATH):
        logger.info(f"Removing existing repository at {LOCAL_REPO_PATH}...")
        # Delete the entire directory
        shutil.rmtree(LOCAL_REPO_PATH)

    logger.info(f"Cloning repository into {LOCAL_REPO_PATH}...")
    return Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)

def modify_file():
    """
    Modifies the specified file (README.md) in the repository by
    writing a timestamped message to it.
    """
    file_path = os.path.join(LOCAL_REPO_PATH, MODIFIED_FILE)
    if os.path.exists(file_path):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        # Open the file in write mode ('w') to clear its content
        with open(file_path, 'w') as file:
            # Write a test message and timestamp to the file
            file.write(f"Test content added on {timestamp}")
    else:
        logger.error(f"File '{MODIFIED_FILE}' not found!")


def commit_and_push(repo):
    """
    Commits changes made to the repository and pushes them to Bitbucket.

    Args:
    repo (Repo): A GitPython Repo object for the cloned repository.

    Returns:
    tuple: The commit hash and the diff of changes.
    """
    # I want to get diff before add files
    diff = repo.git.diff()

    # Stage all changes
    repo.git.add(A=True)

    # Commit changes with a custom message
    commit_hash = repo.index.commit("Automated commit via pytest")

    # Set the remote URL and push the changes
    repo.remotes.origin.set_url(REPO_URL)
    repo.remotes.origin.push()

    logger.info("Changes pushed successfully to Bitbucket.")
    return commit_hash, diff

# Function to validate if the modified file(s) are reflected on Bitbucket after the push
def validate_remote_modified_files(commit_hash, diff):
    """
    Validates if the modified file(s) are reflected on Bitbucket after a push.
    This uses the Bitbucket API to fetch the diff and compares it with the local diff.

    Args:
    commit_hash (str): The commit hash for the changes.
    diff (str): The local diff of changes.

    Returns:
    bool: True if the changes are reflected on Bitbucket, else raises an assertion error.
    """

    # In theory, I could test validation, by clone repo for specific commit to new directory and compare files,
    # But I decided to go with API to check diff, this assumes diff logic works correctly

    # Use the commit hash to get the diff (files modified) from Bitbucket API
    diff_url = f"{BITBUCKET_API_URL}/diff/{commit_hash}"
    response = requests.get(diff_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))

    # Check if the response from the API is successful
    assert response.status_code in [200, 201], f"Failed to retrieve diff: {response.text}"
    changes = response.text

    # Log the diffs for debugging
    logger.debug(f"diff={diff}")
    logger.debug(f"diff={changes}")

    # Diff does not have a newline at the end, but changes have one, so we strip it for comparison
    assert changes[:-1] == diff
    return True

# Complete test function to perform git operations
@allure.epic('Git Operations')
@allure.story('Clone repository, modify file, push changes')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test performs a series of Git operations including cloning a repository, '
    'modifying a file, committing the changes and pushing the new changes to Bitbucket. '
    'It validates if the modified file has been correctly updated on the remote repository.'
)
def test_git_operations(git_operations_fixture):
    """
    Test function that performs the sequence of git operations:
    - Clone the repository.
    - Modify a file.
    - Commit and push the changes.
    - Validate that the changes are reflected in the remote repository.
    """
    # Clone the repository
    repo = clone_repo()

    # Modify the file in the repository
    modify_file()

    # Commit and push changes
    (commit_hash, diff) = commit_and_push(repo)

    # Validate if the changes are reflected on Bitbucket
    assert validate_remote_modified_files(commit_hash, diff), f"File '{MODIFIED_FILE}' was not modified on Bitbucket."

    logger.info("Git operations completed and validated successfully.")

