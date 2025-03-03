import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from ui.pages.LoginPage import LoginPage


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
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=options)
    yield driver
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
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)
    yield driver
