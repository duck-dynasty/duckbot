import locale
from typing import List

import discord
import yfinance
from discord.ext import commands


class Stocks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def stock_info(self, message: discord.Message):
        if not message.author.bot:
            symbols = self.get_stock_symbols(message.content)
            if symbols:
                infos = [self.get_stock_summary(stock) for stock in symbols]
                await message.channel.send("\n".join(infos))

    def get_stock_symbols(self, content: str) -> List[str]:
        # list(dict.fromkeys(x)) removes duplicates but maintains ordering
        return list(dict.fromkeys(word[1:].upper() for word in content.split() if word.startswith("$")))

    def get_stock_summary(self, symbol: str):
        locale.setlocale(locale.LC_MONETARY, "en_US.UTF-8")
        ticker = yfinance.Ticker(symbol)
        info = ticker.info
        price = info["currentPrice"]
        price_s = locale.currency(price, grouping=True)
        currency = info["currency"]
        company = info["shortName"]
        reported_symbol = info["symbol"]
        close = info["previousClose"]
        year_change_percent = f"{'+' if info['52WeekChange'] >= 0 else ''}{round(info['52WeekChange'] * 10000) / 100}"
        daily_change = price - close
        daily_change_percent = f"{'+' if daily_change >= 0 else ''}{round(daily_change / close * 10000) / 100}"
        return f"{reported_symbol} ({company}): {price_s} ({currency}) per share, {daily_change_percent}% today; {year_change_percent}% over a year"
