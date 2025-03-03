import logging
import time

from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec

import config
from ui.pages.BasePage import BasePage

logger = logging.getLogger(__name__)

from enum import Enum


class RepositoryPermission(Enum):
    """
    Enum representing repository permission levels in Bitbucket.
    """
    READ = "Read"
    WRITE = "Write"


class RepositoryPermissionPage(BasePage):
    """
    Represents the repository permissions page in Bitbucket.

    This class provides methods for managing user permissions, including adding,
    modifying, and removing user privileges.
    """
    # EDIT_BUTTON = (By.XPATH, '//main//button[contains(., "Edit")][1]')
    # COMMIT_BUTTON = (By.XPATH, '//form//button[contains(., "Commit")][1]')
    ADD_PRIVILEGE_BUTTON = (By.CSS_SELECTOR, '[data-testid="addPrivilegeButton"]')

    def __init__(self, workspace, repo_name, driver):
        """
        Initializes the RepositoryPermissionPage instance.

        :param workspace: The Bitbucket workspace name.
        :param repo_name: The repository name within the workspace.
        :param driver: The Selenium WebDriver instance.
        """
        super().__init__(f"{config.BITBUCKET_UI_URL}/{workspace}/{repo_name}/admin/permissions", driver)

    def is_page_loaded(self):
        """
        Checks if the file page is loaded by verifying the visibility of the 'Edit' button.

        :return: True if the page is loaded correctly, False otherwise.
        """
        try:
            self.wait.until(ec.element_to_be_clickable(self.ADD_PRIVILEGE_BUTTON))
            return True
        except Exception as e:
            logger.error(e)
            return False

    def add_privilege(self, user):
        """
        Grants repository access to a specified user.

        :param user: The username or email of the user to grant privileges to.
        """
        self.wait.until(ec.element_to_be_clickable(self.ADD_PRIVILEGE_BUTTON)).click()
        x = self.wait.until(ec.element_to_be_clickable(
            (By.XPATH, '//div[contains(., "Add a group or user by name")][1]/following-sibling::div//input[1]')))
        x.send_keys(user)
        # Unfortunately there was not enough time to figure out how they custom list work to wait properly
        time.sleep(3)
        x.send_keys(Keys.ENTER)
        # Click confirm
        self.wait.until(ec.element_to_be_clickable((By.XPATH, '//button[contains(., "Confirm")][1]'))).click()
        self.wait.until(ec.element_to_be_clickable((By.XPATH, f'//tr[contains(., "{user}")][1]')))
        pass

    def change_privilege(self, user, permission: RepositoryPermission):
        """
        Modifies the repository permission level of a given user.

        :param user: The username whose permissions need to be changed.
        :param permission: The new permission level (READ or WRITE).
        """
        user_tr = self.wait.until(ec.element_to_be_clickable((By.XPATH, f'//tr[contains(., "{user}")][1]')))
        perm_dropdown = user_tr.find_element(By.XPATH, './/button[@data-testid="privilegesDropdown--trigger"][1]')
        perm_dropdown.click()
        write = perm_dropdown.find_element(By.XPATH, f'//div//span[contains(., "{permission.value}")][1]')
        write.click()
        self.wait.until(ec.text_to_be_present_in_element(
            (By.XPATH, f'//tr[contains(., "{user}")][1]//button[@data-testid="privilegesDropdown--trigger"][1]'),
            permission.value))

    def remove_user(self, user):
        """
        Removes a user's access from the repository.

        :param user: The username to remove from repository access.
        """
        user_tr = self.wait.until(ec.element_to_be_clickable((By.XPATH, f'//tr[contains(., "{user}")][1]')))
        user_tr.find_element(By.XPATH, './/button[contains(., "Remove")][1]').click()
        self.wait.until(
            ec.element_to_be_clickable((By.CSS_SELECTOR, '[data-testid="remove-access-modal--remove-btn"]'))).click()
        self.wait.until(ec.invisibility_of_element_located((By.XPATH, f'//tr[contains(., "{user}")][1]')))
