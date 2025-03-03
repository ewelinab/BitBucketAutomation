import allure

import config
from api.repositories import Repositories
from ui.pages.FilePage import FilePage
from ui.pages.PullRequestsDiffPage import PullRequestsDiffPage


@allure.epic('UI operations')
@allure.story('Modify file, submit PR, review, and merge')
@allure.severity(allure.severity_level.CRITICAL)
@allure.description(
    'This test performs the following steps: modifying a file in a repository, creating a pull request (PR), '
    'reviewing the PR diff, merging the PR, and validating that the changes have been applied successfully in the repository.'
)
def test_modify_files_and_submit_pr(login):
    """
    This test simulates the process of modifying a file, creating a pull request,
    reviewing and merging the PR, and ensuring that the changes are applied to the repository.
    """
    driver = login
    repo_name = "ui-test-modify_files_and_submit_pr"
    repo = Repositories((config.BITBUCKET_USERNAME, config.BITBUCKET_APP_PASSWORD), config.BITBUCKET_WORKSPACE)
    repo.delete_repository(repo_name)
    repo.create_repositories(repo_name)
    repo.initialize_main_branch(repo_name, "Initial commit to create main",
                                {'README.md': ('README.md', b'a')})

    # Modify Files and Submit Pull Request
    file_page = FilePage(config.BITBUCKET_WORKSPACE, repo_name, "main", "README.md", driver)
    file_page.open()
    assert file_page.get_content() == "a"
    file_page.edit()
    file_page.commit()

    # Create a pull request for the changes
    pr_page = PullRequestsDiffPage(config.BITBUCKET_WORKSPACE, repo_name, 1, driver)
    pr_page.open()

    # Review and Merge Pull Request
    (files, diff) = pr_page.get_diff()
    expected_diff_file_list = 'Modified file\nREADME.md\n+1\n1 line added,\n-1\n1 line removed,'
    expected_file_diff = '@@ -1 +1 @@\n1\na\n1\nab'

    # Validate the file list and diff
    assert files == expected_diff_file_list, "There is something not expected with modified files"
    assert diff == expected_file_diff, "There is something not expected with diff in changed file"

    pr_page.merge()
    file_page.open()
    assert file_page.get_content() == "ab"
