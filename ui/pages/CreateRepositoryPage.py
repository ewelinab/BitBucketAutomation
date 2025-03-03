import logging
from time import sleep

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class RepositoryPage(BasePage):
    """
    Page Object Model (POM) for Bitbucket's Repository Page.
    Provides methods to interact with elements on the repository creation page.
    """
    PROJECT_NAME_DROPDOWN_BUTTON = (By.XPATH, '//div[@id="s2id_id_project"]/a[1]')
    PROJECT_NAME_DROPDOWN_INPUT = (By.ID, "s2id_autogen5_search")
    PROJECT_NAME_DROPDOWN_SPAN = (By.XPATH, "//ul[@class='select2-results']/span[contains(text(), 'Untitled project')]")
    REPO_NAME_INPUT = (By.ID, "id_name")
    CREATE_REPO_BUTTON = (By.XPATH, '//button[contains(text(), "Create repository")]')

    def __init__(self, workspace, driver):
        """
        Initializes the repository page object.

        :param workspace: The Bitbucket workspace where the repository will be created.
        :param driver: The WebDriver instance for interacting with the browser.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/workspace/create/repository", driver)

    def is_page_loaded(self):
        """
        Checks if the repository creation page is loaded by waiting for the 'Create repository' button to be visible.

        :return: True if the page is loaded correctly, False otherwise.
        """
        try:
            self.wait.until(EC.visibility_of_element_located(self.CREATE_REPO_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def open_create_repository_form(self):
        """
        Opens the 'Create repository' form by clicking the corresponding button on the page.
        """
        self.wait.until(EC.element_to_be_clickable(self.CREATE_REPO_BUTTON)).click()
        logger.info("Opened the create repository form")

    def create_repository(self, repo_name):
        """
        Fills in the repository name and submits the repository creation form.

        :param repo_name: The name of the repository to be created.
        """
        select_project = self.wait.until(EC.element_to_be_clickable(self.PROJECT_NAME_DROPDOWN_BUTTON))
        select_project.click()
        # TODO: figure out how to fix loading of items
        sleep(1)

        select_input = self.wait.until(EC.element_to_be_clickable(self.PROJECT_NAME_DROPDOWN_INPUT))
        select_input.send_keys("Untitled project")
        select_input.send_keys(Keys.ENTER)
        self.wait.until(EC.element_to_be_clickable(self.REPO_NAME_INPUT)).send_keys(repo_name)
        self.wait.until(EC.element_to_be_clickable(self.CREATE_REPO_BUTTON)).click()
        logger.info(f"Repository '{repo_name}' creation submitted")
