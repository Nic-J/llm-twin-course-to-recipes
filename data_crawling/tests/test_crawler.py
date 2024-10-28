import pytest

from data_crawling.crawlers.base import BaseCrawler
from data_crawling.utils import get_logger

logger = get_logger(__name__)


class TestBaseCrawler(BaseCrawler):
    def __init__(self, scroll_limit: int = 5) -> None:
        super().__init__(scroll_limit)

    def extract(self, link: str, **kwargs) -> None:
        logger.info(f"Extracting from {link}")


@pytest.fixture(scope="module")
def crawler():
    """Fixture to create a crawler instance for testing."""
    crawler_instance = TestBaseCrawler(scroll_limit=3)
    yield crawler_instance
    crawler_instance.driver.quit()  # Ensure the driver quits after tests


def test_driver_initialization(crawler):
    """Test that the driver is initialized correctly."""
    assert crawler.driver is not None, "Driver should be initialized"


def test_load_page(crawler):
    """Test loading a page with the driver."""
    test_url = "https://www.example.com"
    crawler.driver.get(test_url)

    # Assert that the page title is as expected
    expected_title = "Example Domain"
    actual_title = crawler.driver.title
    assert (
        actual_title == expected_title
    ), f"Title should be '{expected_title}' but was '{actual_title}'"
    actual_title = crawler.driver.title
    assert (
        actual_title == expected_title
    ), f"Title should be '{expected_title}' but was '{actual_title}'"
