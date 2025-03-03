import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class FilePage(BasePage):
    """
    Represents a Bitbucket file page.
    Provides methods to interact with file contents, editing, and committing changes.
    """
    EDIT_BUTTON = (By.XPATH, '//main//button[contains(., "Edit")][1]')
    COMMIT_BUTTON = (By.XPATH, '//form//button[contains(., "Commit")][1]')
    FILE_CONTENT = (By.XPATH, '//div[@data-qa="bk-file__content"]//p[1]')
    COMMIT_FORM = (By.ID, "commit-form")

    def __init__(self, workspace, repo_name, branch_name, file_name, driver):
        """
        Initializes the FilePage object with the specific URL for a given file.

        :param workspace: The Bitbucket workspace where the repository is located.
        :param repo_name: The name of the repository containing the file.
        :param branch_name: The branch name where the file exists.
        :param file_name: The name of the file to be edited.
        :param driver: The WebDriver instance for interacting with the browser.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/src/{branch_name}/{file_name}", driver)

    def is_page_loaded(self):
        """
        Checks if the file page is loaded by verifying the visibility of the 'Edit' button.

        :return: True if the page is loaded correctly, False otherwise.
        """
        try:
            self.wait.until(EC.visibility_of_element_located(self.EDIT_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def can_edit(self):
        """
        Checks if the user has permission to edit the file.

        :return: True if the 'Edit' button is enabled, False otherwise.
        """
        return self.wait.until(EC.visibility_of_element_located(self.EDIT_BUTTON)).is_enabled()

    def edit(self):
        """
        Opens the file for editing. This handles the CodeMirror editor by interacting with its elements.
        The solution here is a workaround due to issues with handling the CodeMirror editor using standard methods.
        """
        # I'm not fan of below solution, but that was only one I was able to find to handle CodeMirror in given time
        self.wait.until(EC.element_to_be_clickable(self.EDIT_BUTTON)).click()
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CodeMirror")))
        code_line = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CodeMirror-line")))
        code_line.click()
        textarea = self.driver.find_element(By.CSS_SELECTOR, ".CodeMirror textarea")
        self.driver.execute_script("arguments[0].value = arguments[1];", textarea, 'b')

    def commit(self):
        """
        Commits the changes made to the file. This involves selecting the 'Create Pull Request' checkbox,
        filling out the branch name, and submitting the commit form.
        """
        self.wait.until(EC.element_to_be_clickable(self.COMMIT_BUTTON)).click()
        commit_form = self.wait.until(EC.visibility_of_element_located(self.COMMIT_FORM))

        pull_request_checkbox = self.wait.until(EC.element_to_be_clickable((By.ID, "id_create-pullrequest")))
        if not pull_request_checkbox.is_selected():
            # Click is intercepted all the time, even that no modal is visible and don't have time to investigate more
            # Pull_request_checkbox.click()
            self.driver.execute_script("arguments[0].click();", pull_request_checkbox)

        branch_name_input = self.wait.until(EC.element_to_be_clickable((By.ID, "id_branch-name")))
        branch_name_input.clear()
        branch_name_input.send_keys("test")

        commit_button = commit_form.find_element(By.XPATH,
                                                 "//div[@class='dialog-button-panel']//button[contains(., 'Commit')]")
        commit_button.click()
        self.wait.until(EC.url_contains("pull-requests"))

    def get_content(self):
        """
        Retrieves the content of the file.

        :return: The text content of the file from the page.
        """
        return self.wait.until(EC.element_to_be_clickable(self.FILE_CONTENT)).text
