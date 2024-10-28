from abc import ABC, abstractmethod
from tempfile import mkdtemp

from aws_lambda_powertools import Logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from data_crawling.config import settings

logger = Logger(service="decodingml/crawler", level=settings.logging_level)


class BaseCrawler(ABC):
    @abstractmethod
    def extract(self, link: str, **kwargs) -> None:
        pass

    def __init__(self, scroll_limit: int = 5) -> None:
        options = webdriver.ChromeOptions()
        options.binary_location = "/opt/chrome/chrome"
        options.add_argument("--no-sandbox")
        options.add_argument("--headless=new")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")

        self.set_extra_driver_options(options)

        self.scroll_limit = scroll_limit
        self.driver = webdriver.Chrome(
            service=webdriver.ChromeService("/opt/chromedriver"),
            options=options,
        )

        logger.info("Crawler initialized successfully")

    def set_extra_driver_options(self, options: Options) -> None:
        pass

    def login(self) -> None:
        pass

    def scroll_page(self) -> None:
        """Scroll through the page based on the scroll limit with a retry mechanism."""
        current_scroll = 0
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        max_retries = 10
        retries = 0

        while True:
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            new_height = self.driver.execute_script("return document.body.scrollHeight")

            # Check if we have reached the bottom of the page
            if new_height == last_height:
                retries += 1
                if retries >= max_retries:  # Avoid hanging indefinitely
                    logger.debug("Max retries reached, stopping scroll.")
                    break
            else:
                retries = 0  # Reset retries if new content was loaded

            last_height = new_height
            current_scroll += 1

            if self.scroll_limit and current_scroll >= self.scroll_limit:
                break
