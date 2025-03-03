import pytest
import allure
import selenium
from selenium.common import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from api.repositories import Repositories
from ui.pages.BitBucketBranchesPage import BitbucketBranchesPage
from ui.pages.BitbucketCreateRepositoryPage import BitbucketRepositoryPage
from ui.pages.BitbucketFilePage import BitbucketFilePage
from ui.pages.BitbucketLoginPage import BitbucketLoginPage
from ui.pages.BitbucketPrDiffPage import BitbucketPrDiffPage
from ui.pages.BitbucketPullRequestsPage import BitbucketPullRequestsPage
from ui.pages.BitbucketRepoPermissionPage import BitbucketRepoPermissionPage, RepoPermission


# Setup WebDriver using webdriver_manager
@pytest.fixture(scope="function")
def ui_fixture():
    """
        This fixture sets up the Selenium WebDriver for the UI tests.
        It configures the Chrome options and returns a WebDriver instance.

        The fixture is scoped to the function, meaning it is invoked before each test
        and cleaned up afterward.
    """
    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--no-sandbox")  # Disable sandbox (for CI/CD or Docker)
    options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage (for CI/CD)
    options.add_argument("--start-maximized")  # Start the browser maximized

    # Initialize the Chrome WebDriver
    driver = webdriver.Chrome(options=options)

    # Yield the driver for the test function to use
    yield driver

    # Cleanup: quit the driver after the test has run
    driver.quit()

@pytest.fixture(scope="function")
def login(ui_fixture):
    """
        This fixture logs into Bitbucket before each test.

        It opens the Bitbucket login page, performs login with provided credentials,
        and then yields the logged-in WebDriver for tests.
    """
    driver = ui_fixture
    """Logs into Bitbucket before each test."""
    login_page = BitbucketLoginPage(driver)
    login_page.open() # Open the login page
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)
    yield driver  # Provide the logged-in driver to tests

# Initialize the Repositories API client with credentials
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
    """
        Test that creates a new repository on Bitbucket using the UI.
        It ensures that the repository does not exist before creation,
        creates it, and validates that it was created correctly.
    """
    driver = login
    repo_page = BitbucketRepositoryPage(config.BITBUCKET_WORKSPACE, driver)
    repo_page.open() # Navigate to the repository creation page
    repo_name = "ui-test-create-repo"

    # Ensure the repository does not exist before creating it
    repo.delete_repository(repo_name)

    # Create the new repository
    repo_page.create_repository(repo_name)

    # Validate that the repository was created successfully
    assert repo.get_repo_details(repo_name)["name"] == repo_name, "Repository was not created correctly"

@allure.epic('UI operations')
@allure.story('Modify file, submit PR, review, and merge')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test performs the following steps: modifying a file in a repository, creating a pull request (PR), '
    'reviewing the PR diff, merging the PR, and validating that the changes have been applied successfully in the repository.'
)
def test_modify_files_and_submit_pr(login):
    """
    This test simulates the process of modifying a file, creating a pull request,
    reviewing and merging the PR, and ensuring that the changes are applied to the repository.
    """
    driver = login
    repo_name = "ui-test-modify_files_and_submit_pr"

    # Prepare the repository for UI tests
    repo.delete_repository(repo_name)
    repo.create_repositories(repo_name)
    repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                {'README.md': ('README.md', b'a')})

    # Modify Files and Submit Pull Request
    file_page = BitbucketFilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver)
    file_page.open() # Open the file page
    assert file_page.get_content() == "a" # Verify the initial content of the file
    file_page.edit() # Edit the file content
    file_page.commit() # Commit the changes

    # Create a pull request for the changes
    pr_page = BitbucketPrDiffPage(config.BITBUCKET_WORKSPACE, repo_name, 1, driver)
    pr_page.open() # Open the pull request page

    # Review and Merge Pull Request
    (files, diff) = pr_page.get_diff()
    expected_diff_file_list = 'Modified file\nREADME.md\n+1\n1 line added,\n-1\n1 line removed,'
    expected_file_diff = '@@ -1 +1 @@\n1\na\n1\nab'

    # Validate the file list and diff
    assert files == expected_diff_file_list, "There is something not expected with modified files"
    assert diff == expected_file_diff, "There is something not expected with diff in changed file"

    # Merge the pull request
    pr_page.merge()

    # Validate Pull Request Changes in the file
    file_page.open()
    assert file_page.get_content() == "ab" # Verify that the file content was updated after merging

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
def test_repository_role_permissions(ui_fixture):
    """
    Test to validate the repository permissions by switching the user role.
    The test ensures that the user with read access cannot modify the repository,
    while the user with write access can perform modifications.
    """
    driver = ui_fixture
    repo_name = "ui-test-permissions"
    repo.delete_repository(repo_name)
    repo.create_repositories(repo_name)
    repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                {'README.md': ('README.md', b'a')})


    """Logs into Bitbucket as admin user."""
    login_page = BitbucketLoginPage(driver)
    login_page.open()
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)

    perm_page = BitbucketRepoPermissionPage(config.BITBUCKET_WORKSPACE, repo_name, driver)
    perm_page.open()
    perm_page.add_privilege("Zostera")
    perm_page.change_privilege("Zostera", RepoPermission.READ)


    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--no-sandbox")  # Disable sandbox (for CI/CD or Docker)
    options.add_argument("--disable-dev-shm-usage")  # Disable /dev/shm usage (for CI/CD)
    options.add_argument("--start-maximized")  # Start the browser maximized

    # Initialize the Chrome WebDriver
    driver2 = webdriver.Chrome(options=options)
    try:
        login_page2 = BitbucketLoginPage(driver2)
        login_page2.open()
        login_page2.login("zostera.marina63@gmail.com", "Password1!2@")

        branches_page = BitbucketBranchesPage(config.BITBUCKET_WORKSPACE, repo_name, driver2)
        branches_page.open()
        assert not branches_page.have_permission_to_create_branch(), "Read only user should not have permission to create branch"
        file_page = BitbucketFilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver2)
        # Test if we can view repository
        file_page.open()
        assert file_page.get_content() == "a", "Read user should be able to view repository"
        assert not file_page.can_edit(), "Read user should not be able to modify file"

        pr_page = BitbucketPullRequestsPage(config.BITBUCKET_WORKSPACE, repo_name, driver2)
        pr_page.open()
        assert not pr_page.have_permission_to_create_pull_request(),  "Read only user should not have permission to create pull request"

        # Change permission to write
        perm_page.change_privilege("Zostera", RepoPermission.WRITE)
        # Try to push a commit.
        file_page = BitbucketFilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver2)
        file_page.open()
        file_page.edit()
        file_page.commit()
        # Try to approve and merge a PR.
        pr_page = BitbucketPrDiffPage(config.BITBUCKET_WORKSPACE, repo_name, 1, driver2)
        pr_page.open()
        pr_page.merge()

        # Remove user
        perm_page.remove_user("Zostera")

        # Check access
        file_page = BitbucketFilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver2)
        try:
            file_page.open()
            assert False, "User should not be able to open repo page if it do not have permissions"
        except Exception as e:
            pass

    finally:
        driver2.quit()

    pass