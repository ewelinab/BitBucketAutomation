import allure

import config
from api.repositories import Repositories
from ui.pages.CreateRepositoryPage import RepositoryPage


@allure.epic('UI operations')
@allure.story('Create a new repository')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test creates a new repository on Bitbucket, ensures the repository does not already exist before creation, '
    'and validates that the repository was created successfully.'
)
def test_create_repository(login):
    """
        Test that creates a new repository on Bitbucket using the UI.
        It ensures that the repository does not exist before creation,
        creates it, and validates that it was created correctly.
    """
    driver = login
    repo = Repositories((config.BITBUCKET_USERNAME, config.BITBUCKET_APP_PASSWORD), config.BITBUCKET_WORKSPACE)
    repo_page = RepositoryPage(config.BITBUCKET_WORKSPACE, driver)
    repo_page.open()
    repo_name = "ui-test-create-repo"
    repo.delete_repository(repo_name)
    repo_page.create_repository(repo_name)
    assert repo.get_repo_details(repo_name)["name"] == repo_name, "Repository is not created properly"
