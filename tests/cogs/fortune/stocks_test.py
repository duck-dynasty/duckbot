from unittest import mock

import pytest
import yfinance

from duckbot.cogs.fortune import Stocks


@pytest.mark.asyncio
async def test_stock_info_bot_author(bot, message):
    message.author.bot = True
    message.content = "$DUX"
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
async def test_stock_info_no_stocks_in_message(bot, message):
    message.content = "bruh, no stocks!"
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    message.channel.send.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["$dux", "$DUX me up so I can do the $dux", "I got me some $dux"])
@mock.patch("yfinance.Ticker")
async def test_stock_info_single_stock(ticker, bot, message, text):
    ticker.return_value.info = info()
    message.content = text
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    ticker.assert_called_once_with("DUX")
    message.channel.send.assert_called_once_with("DUX (Ducks): $100.00 (USD) per share, ($1.00) (-0.99%) today; +10.0% over a year")


@pytest.mark.asyncio
@pytest.mark.parametrize("text", ["$dux1 $dux2", "$DUX1 me up so I can do the $dux2"])
@mock.patch("yfinance.Ticker")
async def test_stock_info_multiple_stocks(ticker, bot, message, text):
    def set_info(sym):
        ticker.return_value.info = info(symbol=sym)

    ticker.side_effect = set_info
    message.content = text
    clazz = Stocks(bot)
    await clazz.stock_info(message)
    ticker.assert_called_with("DUX1")
    ticker.assert_called_with("DUX2")
    message.channel.send.assert_called_once_with("DUX1 (Ducks): $100.00 (USD) per share, ($1.00) (-0.99%) today; +10.0% over a year")


def info(close=101, price=100, year_change=0.1, currency="USD", company="Ducks", symbol="DUX"):
    return {
        "currentPrice": price,
        "currency": currency,
        "shortName": company,
        "symbol": symbol,
        "previousClose": close,
        "52WeekChange": year_change,
    }
