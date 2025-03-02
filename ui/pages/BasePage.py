from abc import ABC, abstractmethod

from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class BasePage(ABC):
    # Every page need to redefined PAGE_URL
    PAGE_URL = ""
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30, poll_frequency=0.2, ignored_exceptions=[NoSuchElementException])

    def open(self):
        """Navigate to the Bitbucket login page"""
        self.driver.get(self.PAGE_URL)
        assert self.is_page_loaded(), "Page was not loaded correctly"

    @abstractmethod
    def is_page_loaded(self):
        """
        Abstract method that should be implemented by subclasses.
        This method should contain logic to check if the page is loaded.
        """
        pass
