from abc import ABC, abstractmethod

from selenium.common import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait


class Page(ABC):
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 30, poll_frequency=0.2, ignored_exceptions=[NoSuchElementException])

    @abstractmethod
    def is_page_loaded(self):
        """
        Abstract method that should be implemented by subclasses.
        This method should contain logic to check if the page is loaded.
        """
        pass
