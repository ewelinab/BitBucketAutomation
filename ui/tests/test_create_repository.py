import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from api.repositories import Repositories
from ui.pages.BitbucketCreateRepositoryPage import BitbucketRepositoryPage
from ui.pages.BitbucketFilePage import BitbucketFilePage
from ui.pages.BitbucketLoginPage import BitbucketLoginPage


# Setup WebDriver using webdriver_manager
@pytest.fixture(scope="module")
def driver():
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
def login(driver):
    """Logs into Bitbucket before each test."""
    login_page = BitbucketLoginPage(driver)
    login_page.open()
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)
    yield driver  # Provide the logged-in driver to tests


repo = Repositories((config.BITBUCKET_USERNAME, config.BITBUCKET_APP_PASSWORD), config.BITBUCKET_WORKSPACE)

def test_create_repository(login):
    driver = login
    repo_page = BitbucketRepositoryPage(config.BITBUCKET_WORKSPACE, driver)
    repo_page.open()
    repo_name = "test-create-ui-repo"

    # we want to be sure that repo does not exist before test
    repo.delete_repository(repo_name)

    repo_page.create_repository(repo_name)
    assert repo.get_repo_details(repo_name)["name"] == repo_name, "Repository was not created correctly"


def test_modify_files_and_submit_pr(login):
    driver = login
    repo_name = "test-modify_files_and_submit_pr"

    # prepare repo for ui tests
    repo.delete_repository(repo_name)
    repo.create_repositories(repo_name)
    repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                {'README.md': ('README.md', b'a')})
    file_page = BitbucketFilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver)
    file_page.open()
    file_page.edit()
    file_page.commit()

    pass


