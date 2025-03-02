import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)


class BitbucketFilePage(BasePage):
    EDIT_BUTTON = (By.XPATH, '//main//button[contains(., "Edit")][1]')
    COMMIT_BUTTON = (By.XPATH, '//form//button[contains(., "Commit")][1]')
    def __init__(self, workspace, repo_name, branch_name, file_name, driver):
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/src/{branch_name}/{file_name}", driver)

    def is_page_loaded(self):
        """Check if the repository page is loaded by verifying the 'Create repository' button"""
        try:
            self.wait.until(EC.visibility_of_element_located(self.EDIT_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def edit(self):
        # I'm not fan of below solution, but that was only one I was able to find to handle CodeMirror in given time
        self.wait.until(EC.element_to_be_clickable(self.EDIT_BUTTON)).click()
        self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CodeMirror")))
        code_line = self.wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "CodeMirror-line")))
        code_line.click()
        textarea = self.driver.find_element(By.CSS_SELECTOR, ".CodeMirror textarea")
        self.driver.execute_script("arguments[0].value = arguments[1];", textarea, 'b')

    def commit(self):
        self.wait.until(EC.element_to_be_clickable(self.COMMIT_BUTTON)).click()
        self.COMMIT_FORM = (By.ID, "commit-form")
        commit_form = self.wait.until(EC.visibility_of_element_located(self.COMMIT_FORM))

        # pull_request_checkbox = commit_form.find_element(By.ID, "id_create-pullrequest")
        pull_request_checkbox = self.wait.until(EC.element_to_be_clickable((By.ID, "id_create-pullrequest")))
        if not pull_request_checkbox.is_selected():  # If the checkbox is not checked
            # click is intercepted all the time, even that no modal is visible and don't have time to investigate more
            #pull_request_checkbox.click()
            self.driver.execute_script("arguments[0].click();", pull_request_checkbox)

        branch_name_input = self.wait.until(EC.element_to_be_clickable((By.ID, "id_branch-name")))
        branch_name_input.clear()
        branch_name_input.send_keys("test")

        commit_button = commit_form.find_element(By.XPATH, "//div[@class='dialog-button-panel']//button[contains(., 'Commit')]")
        commit_button.click()
        self.wait.until(EC.url_contains("pull-requests"))

    def get_content(self):
        self.FILE_CONTENT = (By.XPATH, '//div[@data-qa="bk-file__content"]//p[1]')
        return self.wait.until(EC.element_to_be_clickable(self.FILE_CONTENT)).text
