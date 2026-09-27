import os

import discord
import groq
from discord.ext import commands
from groq.types import Model

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


def is_chat_model(model: Model) -> bool:
    return model.active and "text" in model.output_modalities and "tools" in getattr(model, "supported_features", [])


class Truth(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._ai_client = None

    @property
    def ai_client(self):
        if self._ai_client is None:
            self._ai_client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
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

    @truth.error
    async def on_error(self, context: commands.Context, error):
        await context.send(f"The robot uprising has been postponed due to the following error: {error}")

    def chat_models(self) -> list[Model]:
        models = [m for m in self.ai_client.models.list().data if is_chat_model(m)]
        return sorted(models, key=lambda m: m.created, reverse=True)

    async def fact_check(self, message: discord.Message) -> str:
        message_date = message.edited_at if message.edited_at else message.created_at
        prompt = TRUTH_PROMPT.format(user_name=message.author.display_name, user_message=message.content, date=message_date.strftime("%B %d, %Y"))
        for model in self.chat_models():
            try:
                completion = self.ai_client.chat.completions.create(model=model.id, max_tokens=2000, temperature=0, messages=[{"role": "user", "content": prompt}])
                return completion.choices[0].message.content
            except groq.RateLimitError:
                continue
        raise RuntimeError("every Groq chat model is rate limited or unavailable")
