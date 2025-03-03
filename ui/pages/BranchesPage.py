import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class BranchesPage(BasePage):
    """
    Represents the branches page of a Bitbucket repository.

    This class provides methods to interact with and verify elements
    on the branches page, including checking if the page is loaded
    and verifying branch creation permissions.
    """
    CREATE_BRANCH_BUTTON = (By.ID, 'open-create-branch-modal')

    def __init__(self, workspace, repo_name, driver):
        """
        Initializes the BranchesPage.

        :param workspace: The Bitbucket workspace name.
        :param repo_name: The repository name within the workspace.
        :param driver: The Selenium WebDriver instance.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/branches/", driver)

    def is_page_loaded(self):
        """
        Checks if the file page is loaded by verifying the visibility of the 'Edit' button.

        :return: True if the page is loaded correctly, False otherwise.
        """
        try:
            self.wait.until(EC.visibility_of_element_located(self.CREATE_BRANCH_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def have_permission_to_create_branch(self):
        """
        Checks if the user has permission to create a branch.

        This is determined by checking if the 'Create Branch' button is visible and enabled.

        :return: True if the user can create a branch, False otherwise.
        """
        return self.wait.until(EC.visibility_of_element_located(self.CREATE_BRANCH_BUTTON)).is_enabled()
