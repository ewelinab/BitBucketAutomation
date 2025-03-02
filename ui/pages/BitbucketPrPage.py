import logging

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class BitbucketPrPage(BasePage):
    """
    Provides methods to interact with pull requests such as approving, merging, and retrieving diffs.
    """
    MERGE_BUTTON = (By.XPATH, '//main//button[contains(., "Merge")][1]')
    APPROVE_BUTTON = (By.XPATH, '//main//button[contains(., "Approve")][1]')
    def __init__(self, workspace, repo_name, pr_id, driver):
        """
        Initializes the BitbucketPrPage object with the URL for the specific pull request and the driver.

        :param workspace: The Bitbucket workspace where the repository exists.
        :param repo_name: The name of the repository.
        :param pr_id: The ID of the pull request.
        :param driver: The WebDriver instance for interacting with the browser.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/pull-requests/{pr_id}/diff", driver)

    def is_page_loaded(self):
        """
        Check if the pull request page is loaded by verifying the visibility of the 'Merge' and 'Approve' buttons.

        :return: True if both the 'Merge' and 'Approve' buttons are visible, False otherwise.
        """
        try:
            self.wait.until(EC.visibility_of_element_located(self.MERGE_BUTTON))
            self.wait.until(EC.visibility_of_element_located(self.APPROVE_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def get_diff(self):
        """
        Retrieve the file tree list and diff content from the pull request page.

        :return: A tuple containing the text from the file tree list and the diff content.
        """
        file_tree_list =  self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='file-tree']//li")))
        diff = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//main//div[@class='diff-chunk']")))
        return file_tree_list.text, diff.text

    def merge(self):
        """
        Clicks the 'Merge' button and confirms the merge operation.

        The method will repeatedly try to click the confirmation button in case of a 'StaleElementReferenceException',
        ensuring the merge is confirmed successfully.
        """
        self.wait.until(EC.visibility_of_element_located(self.MERGE_BUTTON)).click()
        self.MERGE_CONFIRMATION_BUTTON=(By.CSS_SELECTOR, '[data-qa="merge-dialog-merge-button"]')
        for _ in range(100):
            try:
                (self.wait.until(EC.element_to_be_clickable(self.MERGE_CONFIRMATION_BUTTON))).click()
                break  # Exit loop if click succeeds
            except StaleElementReferenceException:
                continue
        self.MERGE_WAS_CONFIRMED_SPAN=(By.XPATH, '//div[@data-qa="pr-branches-and-state-styles"]//span[contains(., "Merged")][1]')
        self.wait.until(EC.visibility_of_element_located(self.MERGE_WAS_CONFIRMED_SPAN))

        pass

