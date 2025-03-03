

import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Keys

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class BitbucketBranchesPage(BasePage):
    CREATE_BRANCH_BUTTON = (By.ID, 'open-create-branch-modal')
    def __init__(self, workspace, repo_name, driver):
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
        return self.wait.until(EC.visibility_of_element_located(self.CREATE_BRANCH_BUTTON)).is_enabled()