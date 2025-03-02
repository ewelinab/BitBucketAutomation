import logging

import allure
import pytest

from api.repositories import Repositories
from config import BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD, BITBUCKET_WORKSPACE

logger = logging.getLogger(__name__)

AUTH = (BITBUCKET_USERNAME, BITBUCKET_APP_PASSWORD)

@pytest.fixture(scope="module")
def api_fixture():
    pass

@allure.epic('API operations')
@allure.story('Create repository, initalize "main" branch, create new branch, delete repository')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test checks the basic operations of creating a repository, initializing the "main" branch, '
    'creating a new branch, and deleting the repository in Bitbucket API.'
)

def test_basic_api_operation(api_fixture):
    repo_name = "test_repo_4"
    repo = Repositories(AUTH, BITBUCKET_WORKSPACE)

    repo.create_repositories(repo_name)
    try:
        repo_details = repo.get_repo_details(repo_name);
        assert repo_details["name"] == repo_name

        logger.info("Checking if 'main' branch exists...")
        if not repo.branch_exist(repo_name, "main"):
            repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                        {'README.md': ('README.md', b'# Initial Commit\n')})

        repo.create_branch(repo_name, "test-branch")
    finally:
        assert repo.delete_repository(repo_name), f"Failed to delete repo"

