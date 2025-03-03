import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class PullRequestsPage(BasePage):
    """
    Represents the Pull Requests page in a Bitbucket repository.

    This class provides methods to check if the page is loaded
    and verify permissions for creating pull requests.
    """

    CREATE_PR_BUTTON = (By.XPATH, '//div[@data-qa="create-pull-request-button"]//button')

    def __init__(self, workspace, repo_name, driver):
        """
        Initializes the PullRequestsPage instance.

        :param workspace: The Bitbucket workspace name.
        :param repo_name: The repository name within the workspace.
        :param driver: The Selenium WebDriver instance.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/pull-requests/", driver)

    def is_page_loaded(self):
        """
        Checks if the file page is loaded by verifying the visibility of the 'Edit' button.

        :return: True if the page is loaded correctly, False otherwise.
        """
        try:
            self.wait.until(EC.visibility_of_element_located(self.CREATE_PR_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def have_permission_to_create_pull_request(self):
        """
        Checks if the user has permission to create a pull request.
        This is determined by checking if the 'Create Pull Request' button is visible and enabled.

        :return: True if the user can create a pull request, False otherwise.
        """
        return self.wait.until(EC.visibility_of_element_located(self.CREATE_PR_BUTTON)).is_enabled()
