import datetime
import os

import anthropic
import discord
from discord.ext import commands

from duckbot.util.messages import get_message_reference, try_delete

TRUTH_PROMPT = """Objective: Fact-check the following message from {user_name} on our Discord server and format the response for Discord.

For context, today's date is {date}.

Input: "{user_message}"

Instructions:
1. Analyze the message for factual claims.
2. Verify each claim using only well-established, credible sources.
3. For each claim, provide one of the following responses:
   a) Confirmed: [Brief explanation]
   b) Disputed: [Brief explanation]
   c) Unverified: [Reason why it can't be confirmed or disputed]
4. Do not infer, speculate, or add information beyond what's explicitly stated.
5. Address {user_name} directly in your response.
6. Keep your response concise and clear.
7. If the message contains no factual claims, state that no fact-checking is necessary.
8. Format your response using Discord-friendly markdown:
   - Use **bold** for emphasis
   - Use `code blocks` for quotes or specific terms
   - Use bullet points (•) for lists
   - Keep paragraphs short for readability

Format your response like this:

**Hey {user_name}, I've fact-checked your message:**

- Claim 1: [Verification status]
[Brief explanation]

- Claim 2: [Verification status]
[Brief explanation]

[If applicable] **Note:** [Any important additional information or context]

Remember: Stick to verifiable facts only. If uncertain, state that the information cannot be verified. Ensure the response looks clean and readable in a Discord message."""


class Truth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._ai_client = None

    @property
    def ai_client(self):
        if self._ai_client is None:
            self._ai_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        return self._ai_client

    @commands.command(name="truth")
    async def truth(self, ctx: commands.Context):
        referenced_message = await get_message_reference(ctx.message)
        if referenced_message:
            async with ctx.typing():
                fact_checked_response = await self.fact_check(referenced_message)
                await referenced_message.reply(fact_checked_response)
                await try_delete(ctx.message)
        else:
            await ctx.send("⚠️ Please use this command as a reply to the message you want to fact-check. For example:\n`Reply to a message → !truth`")

    async def fact_check(self, message: discord.Message) -> str:
        try:
            content = message.content
            # Use the message's edited timestamp if it exists, otherwise use created timestamp
            message_date = message.edited_at if message.edited_at else message.created_at
            prompt = TRUTH_PROMPT.format(user_name=message.author.display_name, user_message=content, date=message_date.strftime("%B %d, %Y"))
            message = self.ai_client.messages.create(model="claude-sonnet-4-20250514", max_tokens=1000, temperature=0, messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}])
            return message.content[0].text
        except Exception as e:
            return f"The robot uprising has been postponed due to the following error: {e}"
