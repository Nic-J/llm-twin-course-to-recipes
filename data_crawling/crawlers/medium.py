from dataclasses import dataclass

from aws_lambda_powertools import Logger
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

from data_crawling.config import settings
from data_crawling.crawlers.base import BaseCrawler
from data_crawling.db.documents import ArticleDocument

logger = Logger(service="decodingml/crawler", level=settings.logging_level)


@dataclass
class MediumCrawler(BaseCrawler):
    model: type = ArticleDocument

    def __init__(self, scroll_limit: int = 5) -> None:
        super().__init__(scroll_limit)

    def set_extra_driver_options(self, options) -> None:
        options.add_argument(r"--profile-directory=Profile 2")

    def extract(self, link: str, **kwargs) -> None:
        logger.info(f"Starting scrapping Medium article: {link}")

        try:
            self.driver.get(link)
            self.scroll_page()

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            title = soup.find_all("h1", class_="pw-post-title")
            subtitle = soup.find_all("h2", class_="pw-subtitle-paragraph")

            data = {
                "Title": title[0].string if title else None,
                "Subtitle": subtitle[0].string if subtitle else None,
                "Content": soup.get_text(),
            }

            logger.info(f"Successfully scraped and saved article: {link}")
            self.driver.close()
            instance = self.model(
                platform="medium",
                content=data,
                link=link,
                author_id=kwargs.get("user", ""),
            )
            instance.save()
        except Exception as e:
            logger.error(f"An error occurred: {str(e)}")
            self.driver.close()

    def login(self) -> None:
        """Log in to Medium with Google"""
        self.driver.get("https://medium.com/m/signin")
        self.driver.find_element(By.TAG_NAME, "a").click()
        self.driver.find_element(By.TAG_NAME, "a").click()
