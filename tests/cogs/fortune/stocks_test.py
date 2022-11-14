from unittest import mock

import pytest

from duckbot.cogs.fortune import Stocks


async def test_stock_info_bot_author(bot, message):
    message.author.bot = True
    message.content = "$DUX"
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    message.channel.send.assert_not_called()


async def test_stock_info_no_stocks_in_message(bot, message):
    message.content = "bruh, no stocks!"
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["$dux", "$DUX me up so I can do the $dux", "I got me some $dux"])
@mock.patch("yfinance.Ticker")
async def test_stock_info_single_stock_ignores_duplicates(ticker, bot, message, text):
    ticker.return_value.info = info()
    message.content = text
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    ticker.assert_called_once_with("DUX")
    message.channel.send.assert_called_once_with("DUX (Ducks): **1,000.00** (USD) per share, -0.99% today; +10.0% over a year")


@pytest.mark.parametrize("text", ["$dux", "$DUX me up so I can do the $dux", "I got me some $dux"])
@mock.patch("yfinance.Ticker")
async def test_stock_info_ignores_failed_symbols(ticker, bot, message, text):
    ticker.return_value.info = {}
    message.content = text
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    ticker.assert_called_once_with("DUX")
    message.channel.send.assert_not_called()


@pytest.mark.parametrize("text", ["$dux1 $dux2", "$DUX1 me up so I can do the $dux2"])
@mock.patch("yfinance.Ticker")
async def test_stock_info_multiple_stocks(ticker, bot, message, text):
    dux1 = info(symbol="DUX1")
    dux2 = info(symbol="DUX2", price=100, close=99, year_change=-0.1)

    def set_info(sym):
        ticker.return_value.info = dux1 if sym == "DUX1" else dux2
        return ticker.return_value

    ticker.side_effect = set_info
    message.content = text
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    ticker.assert_any_call("DUX1")
    ticker.assert_any_call("DUX2")
    message.channel.send.assert_called_once_with(
        "DUX1 (Ducks): **1,000.00** (USD) per share, -0.99% today; +10.0% over a year\nDUX2 (Ducks): **100.00** (USD) per share, +1.01% today; -10.0% over a year"
    )


@pytest.mark.parametrize("text", ["$dux1 $dux2", "$DUX1 me up so I can do the $dux2"])
@mock.patch("yfinance.Ticker")
async def test_stock_info_ignores_failed_symbols_when_multiple(ticker, bot, message, text):
    dux1 = info(symbol="DUX1")
    dux2 = {}

    def set_info(sym):
        ticker.return_value.info = dux1 if sym == "DUX1" else dux2
        return ticker.return_value

    ticker.side_effect = set_info
    message.content = text
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    ticker.assert_any_call("DUX1")
    ticker.assert_any_call("DUX2")
    message.channel.send.assert_called_once_with("DUX1 (Ducks): **1,000.00** (USD) per share, -0.99% today; +10.0% over a year")


def info(close=1010, price=1000, year_change=0.1, currency="USD", company="Ducks", symbol="DUX"):
    return {
        "currentPrice": price,
        "currency": currency,
        "shortName": company,
        "symbol": symbol,
        "previousClose": close,
        "52WeekChange": year_change,
    }
