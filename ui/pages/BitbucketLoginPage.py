import logging

import selenium
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ui.pages.Page import Page

logger = logging.getLogger(__name__)


class BitbucketLoginPage(Page):
    # Define locators for the login page
    LOGIN_URL = "https://bitbucket.org/account/signin/"
    USERNAME_FIELD = (By.ID, "username")
    PASSWORD_FIELD = (By.ID, "password")
    CONTINUE_BUTTON = (By.ID, "login-submit")  # Use ID for continue button
    LOGIN_BUTTON = (By.ID, "login-submit")  # Use ID for login button
    PULL_REQUEST_SECTION = (By.XPATH, '//h2[contains(., "Pull requests")]')

    def is_page_loaded(self):
        """
        Check if the login page is loaded by verifying the presence of the username field.
        """
        try:
            self.wait.until(EC.presence_of_element_located(self.USERNAME_FIELD))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def open(self):
        """Navigate to the Bitbucket login page"""
        self.driver.get(self.LOGIN_URL)
        assert self.is_page_loaded(), "Page was not loaded correctly"

    def is_logged_in(self):
        """Validate that login was successful by checking for the pull request section"""
        try:
            assert self.wait.until(EC.visibility_of_element_located(self.PULL_REQUEST_SECTION))
            return True
        except selenium.common.exceptions.TimeoutException as e:
            logger.info("Pull request section was not available in give time. Login was not successful.")
            return False

    def login(self, username, password):
        """Log into Bitbucket with provided credentials"""
        try:
            # Step 1: Enter username and click the continue button
            username_field = self.wait.until(EC.element_to_be_clickable(self.USERNAME_FIELD))
            username_field.send_keys(username)
            continue_button = self.wait.until(EC.element_to_be_clickable(self.CONTINUE_BUTTON))
            continue_button.click()

            # Wait for password field to appear and be clickable and fill it and click login
            password_field = self.wait.until(EC.element_to_be_clickable(self.PASSWORD_FIELD))
            login_button = self.wait.until(EC.element_to_be_clickable(self.LOGIN_BUTTON))
            password_field.send_keys(password)
            login_button.click()

            # Verify login by checking if the user is logged in (e.g., by checking for a logout button)
            assert self.is_logged_in(), "Login failed, Repositories is not visible"
            return True
        except selenium.common.exceptions.TimeoutException as e:
            logger.info(e)
            return False
