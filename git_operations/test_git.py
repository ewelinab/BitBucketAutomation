import os
import requests
import git
import logging
import shutil
import time
from git import Repo
from config import BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, BITBUCKET_WORKSPACE, BASE_URL

logger = logging.getLogger(__name__)

REPO_NAME = "git_test_repo"
BITBUCKET_API_URL = f"https://api.bitbucket.org/2.0/repositories/{BITBUCKET_WORKSPACE}/{REPO_NAME}"


LOCAL_REPO_PATH = ".tmp/git_test_repo"
REPO_URL = f"https://{BITBUCKET_USERNAME}:{BITBUCKET_APP_PASSWORD}@bitbucket.org/{BITBUCKET_WORKSPACE}/{REPO_NAME}.git"
MODIFIED_FILE = "README.md"

def clone_repo():
    if os.path.exists(LOCAL_REPO_PATH):
        logger.info(f"Removing existing repository at {LOCAL_REPO_PATH}...")
        shutil.rmtree(LOCAL_REPO_PATH)  # Delete the entire directory

    logger.info(f"Cloning repository into {LOCAL_REPO_PATH}...")
    return Repo.clone_from(REPO_URL, LOCAL_REPO_PATH)

# Modify a file in the repository
def modify_file():
    file_path = os.path.join(LOCAL_REPO_PATH, MODIFIED_FILE)
    if os.path.exists(file_path):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        # Open the file in write mode ('w') to clear its content
        with open(file_path, 'w') as file:
            # Write a test message and timestamp to the file
            file.write(f"Test content added on {timestamp}")
    else:
        logger.error(f"File '{MODIFIED_FILE}' not found!")

# Commit and push changes to Bitbucket
def commit_and_push(repo):
    # we want to get diff before add files
    diff = repo.git.diff()
    repo.git.add(A=True)  # Stage all changes
    commit_hash = repo.index.commit("Automated commit via pytest")  # Commit changes
    repo.remotes.origin.set_url(REPO_URL)
    repo.remotes.origin.push()
    logger.info("Changes pushed successfully to Bitbucket.")
    return commit_hash, diff

# Validate if the modified file(s) are reflected on Bitbucket after the push
def validate_remote_modified_files(commit_hash, diff):

    # in theory, we could test validation, by clone repo for specific commit to new directory and compare files,
    # but I decided to go with API to check diff, this assumes diff logic works correctly

    # Use the commit hash to get the diff (files modified)
    diff_url = f"{BITBUCKET_API_URL}/diff/{commit_hash}"
    response = requests.get(diff_url, auth=(BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD))

    # check if commit exist
    assert response.status_code in [200, 201], f"Failed to retrieve diff: {response.text}"
    changes = response.text

    # check modified files
    logger.debug(f"diff={diff}")
    logger.debug(f"diff={changes}")

    # diff do not have in the end new line, and changes have one so we want to check just changes without last char
    assert changes[:-1] == diff
    return True

# Complete test function
def test_git_operations():
    repo = clone_repo()
    modify_file()
    (commit_hash, diff) = commit_and_push(repo)
    assert validate_remote_modified_files(commit_hash, diff), f"File '{MODIFIED_FILE}' was not modified on Bitbucket."
    logger.info("Git operations completed and validated successfully.")

