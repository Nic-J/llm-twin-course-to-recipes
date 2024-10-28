import re
from dataclasses import dataclass, field

from data_crawling.crawlers.base import BaseCrawler


@dataclass
class CrawlerDispatcher:
    _crawlers: dict[str, type[BaseCrawler]] = field(default_factory=dict)

    def register(self, domain: str, crawler: type[BaseCrawler]) -> None:
        self._crawlers[r"https://(www\.)?{}.com/*".format(re.escape(domain))] = crawler

    def get_crawler(self, url: str) -> BaseCrawler:
        for pattern, crawler in self._crawlers.items():
            if re.match(pattern, url):
                return crawler()
        else:
            raise ValueError("No crawler found for the provided link")
