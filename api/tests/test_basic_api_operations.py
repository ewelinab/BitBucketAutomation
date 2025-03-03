import logging

import allure
import pytest

from api.repositories import Repositories
from config import BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, BITBUCKET_WORKSPACE

# Initialize logger for the module
logger = logging.getLogger(__name__)

# Authentication tuple for Bitbucket API using username and app password
AUTH = (BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)


@pytest.fixture(scope="module")
def api_fixture():
    """
    Fixture for setting up any necessary resources for API tests.
    """
    pass


@allure.epic('API operations')
@allure.story('Create repository, initialize "main" branch, create new branch, delete repository')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test checks the basic operations of creating a repository, initializing the "main" branch, '
    'creating a new branch, and deleting the repository in Bitbucket API.'
)
def test_basic_api_operation(api_fixture):
    """
    This test validates the following basic repository operations via the Bitbucket API:
    1. Creating a repository.
    2. Initializing the 'main' branch if it does not exist.
    3. Creating a new branch called "test-branch."
    4. Deleting the repository after the operations.

    The test ensures that these API operations are performed correctly.
    """
    # Initialize the Repositories API client
    repo = Repositories(AUTH, BITBUCKET_WORKSPACE)
    repo_name = "test-api-repo"

    repo.delete_repository(repo_name)

    # Create the repository
    repo.create_repositories(repo_name)
    try:
        # Get the repository details and verify the repository was created
        repo_details = repo.get_repo_details(repo_name)
        assert repo_details["name"] == repo_name

        logger.info("Checking if 'main' branch exists...")

        # If the 'main' branch does not exist, initialize it with a commit
        if not repo.branch_exist(repo_name, "main"):
            repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                        {'README.md': ('README.md', b'# Initial Commit\n')})

        # Create a new branch named "test-branch"
        repo.create_branch(repo_name, "test-branch")
    finally:
        # Delete the repository after the operations are complete
        assert repo.delete_repository(repo_name), f"Failed to delete repo"
