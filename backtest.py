import csv
import logging
from datetime import datetime
from decimal import Decimal
from pprint import pprint

logger = logging.getLogger(__file__)

POSTS: list[tuple[str, str]] = [
    ('20.03.2024', 'EQIX'),
    ('15.03.2024', 'LPP.WA'),
    ('15.02.2024', 'TEMN.SW'),
    ('13.02.2024', 'RENB'),
    ('01.02.2024', 'LFST'),
    ('07.11.2023', 'EH'),
    ('31.08.2023', 'TIO'),
    ('15.08.2023', 'FRHC'),
    ('06.06.2023', 'TIO'),
    ('02.05.2023', 'IEP'),
    ('23.03.2023', 'SQ'),
    ('07.12.2022', 'WELL'),
    ('19.10.2022', 'ESTA'),
    ('16.06.2022', 'EBIXQ'),
]
BUY_OFFSET: int = 2  # покупаем через день после новости от гиденбурга
STOP_LOSS_OFFSET: int = 22  # если за указанные дни не продали - выходим по рынку
PROFIT_PERCENT: Decimal = Decimal(30)  # минимальный профит для заявки на продажу
INIT_DEPOSIT: Decimal = Decimal(1000)


def main() -> tuple[dict[str, Decimal], Decimal]:
    counter = {}
    parsed_posts: list[tuple[datetime, str]] = [
        (datetime.strptime(date_str, '%d.%m.%Y'), ticker)
        for date_str, ticker in POSTS
    ]

    deposit_left: Decimal = INIT_DEPOSIT

    for init_date, ticker in parsed_posts:
        profit_loss_percent: Decimal = backtest_post(ticker, init_date)
        deposit_left += deposit_left * profit_loss_percent / Decimal(100)
        logger.info('ticker %s: %.2f%% and deposit after is %d', ticker, profit_loss_percent, deposit_left)
        counter[ticker] = profit_loss_percent

    return counter, deposit_left


def backtest_post(ticker: str, first_date: datetime) -> Decimal:
    with open(f'quotes/{ticker}.csv', 'r') as file:
        ticker_quotes = [
            # date, high, low
            (datetime.strptime(row[0], '%Y-%m-%d'), Decimal(row[2]), Decimal(row[3]))
            for index, row in enumerate(csv.reader(file))
            if index
        ]
    ticker_quotes: list[tuple[datetime, Decimal, Decimal]] = [
        quote
        for quote in ticker_quotes
        if quote[0] >= first_date
    ]

    buy_quote: Decimal = Decimal(0)
    sell_quote: Decimal = Decimal(0)
    for day_num, quote in enumerate(ticker_quotes):
        average_quote = (quote[1] + quote[2]) / 2
        high_quote = quote[1]
        lower_quote = quote[2]
        if day_num < BUY_OFFSET:  # skip post-date
            continue

        if day_num == BUY_OFFSET:
            buy_quote = high_quote  # bough by high price
            logger.info('bough by %.2f', buy_quote)
            continue

        if day_num > STOP_LOSS_OFFSET:
            sell_quote = lower_quote  # sold by lower market price
            logger.info('sold by %.2f (stop loss)', sell_quote)
            break

        take_profit_price = buy_quote + buy_quote / Decimal(100) * PROFIT_PERCENT
        logger.info('take profit %.2f', take_profit_price)

        if high_quote >= take_profit_price:
            sell_quote = average_quote  # sold by average market price of day
            logger.info('sold by %.2f (take profit)', sell_quote)
            break

    if not sell_quote:
        sell_quote = (ticker_quotes[-1][1] + ticker_quotes[-1][2]) / 2  # sold by lower market price of last day
        logger.info('sold by %.2f (stop loss)', sell_quote)

    one_percent = buy_quote / Decimal(100)
    return (sell_quote - buy_quote) / one_percent


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    results, deposit = main()
    pprint(results, indent=4)
    print('total percent %.2f' % sum(results.values()))
    print(f'deposit init {INIT_DEPOSIT}')
    print(f'deposit left {deposit}')
