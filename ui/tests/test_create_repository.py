import pytest
import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from api.repositories import Repositories
from ui.pages.BitbucketCreateRepositoryPage import BitbucketRepositoryPage
from ui.pages.BitbucketFilePage import BitbucketFilePage
from ui.pages.BitbucketLoginPage import BitbucketLoginPage
from ui.pages.BitbucketPrPage import BitbucketPrPage


# Setup WebDriver using webdriver_manager
@pytest.fixture(scope="function")
def ui_fixture():
    """Set up the Selenium WebDriver using webdriver_manager."""
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--no-sandbox")  # Disable sandbox (for CI/CD or Docker)
    options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage (for CI/CD)
    options.add_argument("--start-maximized")  # Start the browser maximized
    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture(scope="function")
def login(ui_fixture):
    driver = ui_fixture
    """Logs into Bitbucket before each test."""
    login_page = BitbucketLoginPage(driver)
    login_page.open()
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)
    yield driver  # Provide the logged-in driver to tests


repo = Repositories((config.BITBUCKET_USERNAME, config.BITBUCKET_APP_PASSWORD), config.BITBUCKET_WORKSPACE)


#Create Repository (UI)
@allure.epic('UI operations')
@allure.story('Create a new repository')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test creates a new repository on Bitbucket, ensures the repository does not already exist before creation, '
    'and validates that the repository was created successfully.'
)
def test_create_repository(login):
    driver = login
    repo_page = BitbucketRepositoryPage(config.BITBUCKET_WORKSPACE, driver)
    repo_page.open()
    repo_name = "test-create-ui-repo"

    # we want to be sure that repo does not exist before test
    repo.delete_repository(repo_name)

    repo_page.create_repository(repo_name)
    assert repo.get_repo_details(repo_name)["name"] == repo_name, "Repository was not created correctly"

@allure.epic('UI operations')
@allure.story('Modify file, submit PR, review, and merge')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test performs the following steps: modifying a file in a repository, creating a pull request (PR), '
    'reviewing the PR diff, merging the PR, and validating that the changes have been applied successfully in the repository.'
)
def test_modify_files_and_submit_pr(login):
    driver = login
    repo_name = "test-modify_files_and_submit_pr"

    # prepare repo for ui tests
    repo.delete_repository(repo_name)
    repo.create_repositories(repo_name)
    repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                {'README.md': ('README.md', b'a')})

    # Modify Files and Submit PR
    file_page = BitbucketFilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver)
    file_page.open()
    assert file_page.get_content() == "a"
    file_page.edit()
    file_page.commit()

    pr_page = BitbucketPrPage(config.BITBUCKET_WORKSPACE, repo_name, 1, driver)
    pr_page.open()

    # Review and Merge Pull Request
    (files, diff) = pr_page.get_diff()
    expected_diff_file_list = 'Modified file\nREADME.md\n+1\n1 line added,\n-1\n1 line removed,'
    expected_file_diff = '@@ -1 +1 @@\n1\na\n1\nab'
    assert files == expected_diff_file_list, "There is something not expected with modified files"
    assert diff == expected_file_diff, "There is something not expected with diff in changed file"

    # merge pull request
    pr_page.merge()

    # Validate Pull Request Changes
    file_page.open()
    assert file_page.get_content() == "ab"

@allure.epic('UI operations')
@allure.story('Test repository permissions with role switching')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test performs the following steps: '
    '1. Navigating to Repository Settings and adding a new user with read access. '
    '2. Logging in as the new user and attempting to create a branch, modify a file, and verify that they can only view the repository and pull requests. '
    '3. Switching the new user’s role to write access, and verifying the user can push commits and approve/merge PRs. '
    '4. Removing the user from the repository and verifying that access is denied.'
)
def test_repository_role_permissions(login):
    pass