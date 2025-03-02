import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from ui.pages.BitbucketCreateRepositoryPage import BitbucketRepositoryPage
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


def test_create_repository(driver):
    # Log into Bitbucket
    login_page = BitbucketLoginPage(driver)
    login_page.open()
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)

    repo_page = BitbucketRepositoryPage(config.BITBUCKET_WORKSPACE, driver)
    repo_page.open()
    repo_page.create_repository("test11113")

