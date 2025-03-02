import logging

from selenium.common import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class BitbucketPrPage(BasePage):
    MERGE_BUTTON = (By.XPATH, '//main//button[contains(., "Merge")][1]')
    APPROVE_BUTTON = (By.XPATH, '//main//button[contains(., "Approve")][1]')
    def __init__(self, workspace, repo_name, pr_id, driver):
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/pull-requests/{pr_id}/diff", driver)

    def is_page_loaded(self):
        """Check if the repository page is loaded by verifying the 'Create repository' button"""
        try:
            self.wait.until(EC.visibility_of_element_located(self.MERGE_BUTTON))
            self.wait.until(EC.visibility_of_element_located(self.APPROVE_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def get_diff(self):
        file_tree_list =  self.wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='file-tree']//li")))
        diff = self.wait.until(EC.visibility_of_element_located((By.XPATH, "//main//div[@class='diff-chunk']")))
        return file_tree_list.text, diff.text

    def merge(self):
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

