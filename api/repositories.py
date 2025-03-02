import logging

import requests

import config

logger = logging.getLogger(__name__)


class Repositories:
    """
    A class that provides methods for interacting with Bitbucket repositories via API.
    It supports creating repositories, fetching repository details, checking branches,
    initializing branches, and deleting repositories.
    """

    # Base URL for the Bitbucket repository API
    REPO_BASE_URL = f"{config.BASE_API_URL}/repositories"

    def __init__(self, auth, workspace):
        """
        Initializes the Repositories object with authentication credentials and workspace.

        :param auth: Tuple containing the username and app password for authentication.
        :param workspace: The Bitbucket workspace where the repository will be created or accessed.
        """
        self.workspace = workspace
        self.auth = auth
        super().__init__()

    def create_repositories(self, repo_name):
        """
        Creates a new repository in the specified workspace.

        :param repo_name: The name of the repository to be created.
        """
        url = f"{self.REPO_BASE_URL}/{self.workspace}/{repo_name}"

        # I do not define project so it will be assigned to last used one
        payload = {
            "scm": "git",
            "is_private": True
        }

        logger.info(f"Creating repository using url: {url}")
        response = requests.post(url, json=payload, auth=self.auth)
        logger.debug(f"Response: {response.status_code} - {response.text}")
        assert response.status_code in [200, 201], f"Failed to create repo: {response.text}"
        assert response.json().get("name") == repo_name

    def get_repo_details(self, repo_name):
        """
        Fetches details for a specified repository.

        :param repo_name: The name of the repository to fetch details for.
        :return: The JSON response containing repository details.
        """
        url = f"{self.REPO_BASE_URL}/{self.workspace}/{repo_name}"

        logger.info(f"Fetching repository details: {repo_name}")
        response = requests.get(url, auth=self.auth)

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            logger.warning(f"Repository access denied. response={response.text}")
        elif response.status_code == 404:
            logger.warning(f"Repository not found. response={response.text}")

        # All other codes are unexpected, so I want to raise exception
        response.raise_for_status()

    def branch_exist(self, repo_name, branch_name):
        """
        Checks if a specific branch exists in the repository.

        :param repo_name: The name of the repository.
        :param branch_name: The name of the branch to check.
        :return: True if the branch exists, False if it does not.
        """
        url = f"{self.REPO_BASE_URL}/{self.workspace}/{repo_name}/refs/branches/{branch_name}"
        logger.debug(f"GET Request URL: {url}")
        response = requests.get(url, auth=self.auth)
        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")

        if response.status_code == 200:
            return True
        elif response.status_code == 404:
            return False

        # All other codes are unexpected, so I want to raise exception
        response.raise_for_status()

    def initialize_main_branch(self, repo_name, commit_name, files):
        """
        Initializes the 'main' branch in the repository with an initial commit.

        :param repo_name: The name of the repository.
        :param commit_name: The commit message to use for the initial commit.
        :param files: The files to include in the commit.
        """
        logger.info("Initializing 'main' branch with an initial commit...")
        url = f"{self.REPO_BASE_URL}/{self.workspace}/{repo_name}/src"
        payload = {
            "message": commit_name,
            "branch": "main"
        }

        logger.debug(f"POST Request URL: {url}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(url, auth=self.auth, data=payload, files=files)

        logger.info(f"Response Status: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")

        if response.status_code == 201:
            logger.info("✅ Successfully initialized 'main' branch with initial commit.")
        else:
            logger.error(f"❌ Failed to initialize 'main' branch: {response.text}")
            response.raise_for_status()

    def create_branch(self, repo_name, branch_name):
        """
        Creates a new branch in the repository from the 'main' branch.

        :param repo_name: The name of the repository.
        :param branch_name: The name of the branch to create.
        """
        url = f"{self.REPO_BASE_URL}/{self.workspace}/{repo_name}/refs/branches"
        payload = {"name": branch_name, "target": {"hash": "main"}}

        logger.debug(f"POST Request URL: {url}")
        logger.debug(f"Payload: {payload}")

        response = requests.post(url, json=payload, auth=self.auth)

        logger.debug(f"Response Status: {response.status_code}")
        logger.debug(f"Response Body: {response.text}")

        if response.status_code == 201:
            logger.info(f"✅ Successfully created the '{branch_name}' branch from 'main'.")
        else:
            logger.error(f"❌ Failed to create branch '{branch_name}': {response.text}")
            response.raise_for_status()

    def delete_repository(self, repo_name):
        """
        Deletes the specified repository from the workspace.

        :param repo_name: The name of the repository to delete.
        :return: True if the repository is deleted successfully, False otherwise.
        """
        url = f"{self.REPO_BASE_URL}/{self.workspace}/{repo_name}/"
        logger.info(f"Deleting repository: {repo_name}")
        response = requests.delete(url, auth=self.auth)

        logger.debug(f"Response: {response.status_code} - {response.text}")
        return response.status_code == 204