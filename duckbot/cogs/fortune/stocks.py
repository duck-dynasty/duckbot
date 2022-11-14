from typing import List, Optional

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
                summaries = [self.get_stock_summary(ticker) for ticker in map(self.get_ticker, symbols) if ticker]
                if summaries:
                    await message.channel.send("\n".join(summaries))

    def get_stock_symbols(self, content: str) -> List[str]:
        # list(dict.fromkeys(x)) removes duplicates but maintains ordering
        return list(dict.fromkeys(word[1:].upper() for word in content.split() if word.startswith("$")))

    def get_ticker(self, symbol: str) -> Optional[yfinance.Ticker]:
        ticker = yfinance.Ticker(symbol)
        return ticker if ticker.info.get("symbol", None) else None

    def get_stock_summary(self, ticker: yfinance.Ticker):
        info = ticker.info
        price = info["currentPrice"]
        currency = info["currency"]
        company = info["shortName"]
        reported_symbol = info["symbol"]
        close = info["previousClose"]
        year_change_percent = f"{'+' if info['52WeekChange'] >= 0 else ''}{round(info['52WeekChange'] * 10000) / 100}"
        daily_change = price - close
        daily_change_percent = f"{'+' if daily_change >= 0 else ''}{round(daily_change / close * 10000) / 100}"
        return f"{reported_symbol} ({company}): **{price:,.2f}** ({currency}) per share, {daily_change_percent}% today; {year_change_percent}% over a year"
