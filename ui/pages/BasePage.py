from abc import ABC, abstractmethod

from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class BasePage(ABC):
    """
    A base class that should be inherited by all page classes in the framework.
    It provides common functionality such as opening a page and waiting for it to load.
    """

    def __init__(self, page_url, driver):
        """
        Initializes the base page with the provided URL and WebDriver instance.

        :param page_url: The URL of the page to navigate to.
        :param driver: The WebDriver instance used to interact with the page.
        """
        self.page_url = page_url
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30, poll_frequency=0.2, ignored_exceptions=[NoSuchElementException])

    def open(self):
        """
        Navigates to the page URL and ensures that the page is loaded.

        This method uses the `is_page_loaded` method to verify if the page was loaded correctly.
        If the page is not loaded correctly, an assertion error will be raised.
        """
        self.driver.get(self.page_url)
        assert self.is_page_loaded(), "Page is not loaded correctly"

    @abstractmethod
    def is_page_loaded(self):
        """
        Abstract method that should be implemented by subclasses to check if the page is loaded.

        Subclasses must define this method with the logic that verifies the page has loaded correctly.
        This method should return True if the page is fully loaded, otherwise False.
        """
        pass
