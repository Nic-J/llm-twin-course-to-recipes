from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

from data_crawling import lib
from data_crawling.config import settings
from data_crawling.crawlers.linkedin import LinkedInCrawler
from data_crawling.crawlers.medium import MediumCrawler
from data_crawling.db.documents import UserDocument
from data_crawling.dispatcher import CrawlerDispatcher

logger = Logger(service="decodingml/crawler", level=settings.logging_level)

_dispatcher = CrawlerDispatcher()
_dispatcher.register("medium", MediumCrawler)
_dispatcher.register("linkedin", LinkedInCrawler)


def handler(event: dict[str, Any], context: LambdaContext | None) -> dict[str, Any]:
    first_name, last_name = lib.user_to_names(event.get("user"))

    user = UserDocument.get_or_create(first_name=first_name, last_name=last_name)

    link = event.get("link")

    if link is None:
        return {"statusCode": 400, "body": "No link provided"}

    crawler = _dispatcher.get_crawler(link)

    try:
        crawler.extract(link=link, user=user)
        return {"statusCode": 200, "body": "Link processed successfully"}

    except Exception as e:
        return {"statusCode": 500, "body": f"An error occurred: {str(e)}"}


if __name__ == "__main__":
    event = {
        "user": "Nicolas Jadot",
        "link": "https://www.linkedin.com/in/njadot/",
    }
    handler(event, None)
