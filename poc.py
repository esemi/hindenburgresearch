import logging
import re
from dataclasses import dataclass
from decimal import Decimal

import feedparser
import pendulum

MARKET_QUOTE_OFFSET_DAYS: int = 7
LIMIT: int = 1
RSS_FEED_URL: str = 'https://hindenburgresearch.com/feed/'
QUOTES_FREE_APIKEY: str = 'E4LY6VGDX9M9QUIN'

logger = logging.getLogger(__file__)

ticket_pattern = re.compile(r'\(([A-Z]+:[A-Z]+)\)')
row_template = '{0} {1}: init quote {2}, minimal quote {3}'


@dataclass
class Post:
    created_at: pendulum.DateTime
    link: str
    title: str
    ticker: str


@dataclass
class TickerQuote:
    init_quote: Decimal
    minimal_quote: Decimal


def main() -> None:
    posts: list[Post] = get_posts(LIMIT)
    logger.info('found %d posts', len(posts))

    # todo notify if new post


def get_posts(limit: int) -> list[Post]:
    feed = feedparser.parse(RSS_FEED_URL)
    entities: list[Post] = []
    for entry in feed.entries[:limit]:
        logger.info('parse entry: %s', entry.link)

        if ticker := _parse_ticker(entry.summary):
            entities.append(Post(
                created_at=pendulum.parse(entry.published, strict=False, tz='UTC'),
                link=entry.link,
                title=entry.title,
                ticker=ticker,
            ))

    return entities[::-1]


def _parse_ticker(source: str) -> str | None:
    if match := ticket_pattern.search(source):
        return match.group(1)
    return None


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
