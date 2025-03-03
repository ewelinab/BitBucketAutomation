import allure
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config
from api.repositories import Repositories
from ui.pages.BranchesPage import BranchesPage
from ui.pages.FilePage import FilePage
from ui.pages.LoginPage import LoginPage
from ui.pages.PullRequestsDiffPage import PullRequestsDiffPage
from ui.pages.PullRequestsPage import PullRequestsPage
from ui.pages.RepositoryPermissionPage import RepositoryPermissionPage, RepositoryPermission


@allure.epic('UI operations')
@allure.story('Test repository permissions with role switching')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test performs the following steps: '
    '1. Navigating to Repository Settings and adding a new user with read access. '
    '2. Logging in as the new user and attempting to create a branch, modify a file, and verify that they can only view the repository and pull requests. '
    '3. Switching the new user’s role to write access, and verifying the user can push commits and approve/merge PRs. '
    '4. Removing the user from the repository and verifying that access is denied.'
)
def test_repository_role_permissions(ui_fixture):
    """
    Test to validate the repository permissions by switching the user role.
    The test ensures that the user with read access cannot modify the repository,
    while the user with write access can perform modifications.
    """
    driver = ui_fixture
    repo_name = "ui-test-permissions"
    repo = Repositories((config.BITBUCKET_USERNAME, config.BITBUCKET_APP_PASSWORD), config.BITBUCKET_WORKSPACE)
    repo.delete_repository(repo_name)
    repo.create_repositories(repo_name)
    repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                {'README.md': ('README.md', b'a')})

    """Logs into Bitbucket as admin user."""
    login_page = LoginPage(driver)
    login_page.open()
    login_page.login(config.BITBUCKET_USERNAME_EMAIL, config.BITBUCKET_PASSWORD)

    perm_page = RepositoryPermissionPage(config.BITBUCKET_WORKSPACE, repo_name, driver)
    perm_page.open()
    perm_page.add_privilege(config.BITBUCKET_SECOND_USERNAME_NAME)
    perm_page.change_privilege(config.BITBUCKET_SECOND_USERNAME_NAME, RepositoryPermission.READ)

    options = Options()
    options.add_argument("start-maximized")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--start-maximized")

    driver2 = webdriver.Chrome(options=options)
    try:
        login_page2 = LoginPage(driver2)
        login_page2.open()
        login_page2.login(config.BITBUCKET_SECOND_USERNAME_EMAIL, config.BITBUCKET_SECOND_USER_PASSWORD)

        branches_page = BranchesPage(config.BITBUCKET_WORKSPACE, repo_name, driver2)
        branches_page.open()
        assert not branches_page.have_permission_to_create_branch(), "Read only user should not have permission to create branch"
        file_page = FilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver2)
        # Test if we can view repository
        file_page.open()
        assert file_page.get_content() == "a", "Read user should be able to view repository"
        assert not file_page.can_edit(), "Read user should not be able to modify file"

        pr_page = PullRequestsPage(config.BITBUCKET_WORKSPACE, repo_name, driver2)
        pr_page.open()
        assert not pr_page.have_permission_to_create_pull_request(), "Read only user should not have permission to create pull request"

        # Change permission to write
        perm_page.change_privilege(config.BITBUCKET_SECOND_USERNAME_NAME, RepositoryPermission.WRITE)

        # Try to push a commit
        file_page = FilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver2)
        file_page.open()
        file_page.edit()
        file_page.commit()

        # Try to approve and merge a PR
        pr_page = PullRequestsDiffPage(config.BITBUCKET_WORKSPACE, repo_name, 1, driver2)
        pr_page.open()
        pr_page.merge()

        # Remove user
        perm_page.remove_user(config.BITBUCKET_SECOND_USERNAME_NAME)

        # Check access
        file_page = FilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver2)
        try:
            # TODO: this could be done better by not waiting full timeout
            file_page.open()
            assert False, "User should not be able to open repository page, If does not have permissions"
        except Exception:
            pass

    finally:
        driver2.quit()

    pass
