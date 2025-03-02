from abc import ABC, abstractmethod

from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class BasePage(ABC):
    """
    Class used to be inherited by all Pages in our framework
    """

    def __init__(self, page_url, driver):
        """
        :param page_url: page url that will be used when page is open
        :param driver: webdriver instance
        """
        self.page_url = page_url
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30, poll_frequency=0.2, ignored_exceptions=[NoSuchElementException])

    def open(self):
        """Navigate to page url"""
        self.driver.get(self.page_url)
        assert self.is_page_loaded(), "Page was not loaded correctly"

    @abstractmethod
    def is_page_loaded(self):
        """
        Abstract method that should be implemented by subclasses.
        This method should contain logic to check if the page is loaded.
        Should return True if page was loaded.
        """
        pass
