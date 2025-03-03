import logging

import selenium
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    """
    Provides methods for logging into Bitbucket, checking login status, and verifying successful login.
    """
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    CONTINUE_BUTTON = (By.ID, "login-submit")
    LOGIN_BUTTON = (By.ID, "login-submit")
    PULL_REQUEST_SECTION = (By.XPATH, '//h2[contains(., "Pull requests")]')

    def __init__(self, driver):
        """
        Initializes the LoginPage object with the URL for the login page and the driver.

        :param driver: The WebDriver instance for interacting with the browser.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/account/signin/", driver)

    def is_page_loaded(self):
        """
        Checks if the login page is loaded by verifying the presence of the username field.

        :return: True if the username field is present (indicating the page is loaded), False otherwise.
        """
        try:
            self.wait.until(EC.presence_of_element_located(self.USERNAME_FIELD))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def is_logged_in(self):
        """
        Validates that the login was successful by checking for the presence of the 'Pull requests' section.

        :return: True if the user is logged in (i.e., the pull request section is visible), False otherwise.
        """
        try:
            assert self.wait.until(EC.visibility_of_element_located(self.PULL_REQUEST_SECTION))
            return True
        except selenium.common.exceptions.TimeoutException as e:
            logger.info("Pull request section was not available in give time. Login was not successful")
            return False

    def login(self, username, password):
        """
        Logs into Bitbucket with the provided username and password.

        :param username: The Bitbucket username for login.
        :param password: The Bitbucket password for login.

        :return: True if the login is successful, False otherwise.
        """
        try:
            username_field = self.wait.until(EC.element_to_be_clickable(self.USERNAME_FIELD))
            username_field.send_keys(username)
            continue_button = self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
            continue_button.click()

            password_field = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_FIELD))
            login_button = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
            password_field.send_keys(password)
            login_button.click()

            # Verify login by checking if the user is logged in
            assert self.is_logged_in(), "Login failed, Repositories is not visible"
            return True
        except selenium.common.exceptions.TimeoutException as e:
            logger.info(e)
            return False
