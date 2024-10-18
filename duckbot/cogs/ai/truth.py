import discord
import anthropic
from discord.ext import commands

CLIENT = anthropic.Anthropic(
    api_key="mu key",
)
PROMPT = """Objective: Fact-check the following message from {user_name} on our Discord server and format the response for Discord.

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

    @commands.command(name="truth")
    async def truth(self, ctx: commands.Context):
        message = ctx.message
        if message.reference:
            try:
                referenced_message = await message.channel.fetch_message(message.reference.message_id)
            except (discord.errors.NotFound, discord.errors.Forbidden):
                await ctx.send("I can't find the TRUTH if you don't give me the message to fact-check.")
                return
            fact_checked_response = self.fact_check(referenced_message)
            await message.reply(fact_checked_response)
        else:
            await ctx.send("⚠️ Please use this command as a reply to the message you want to fact-check. For example:\n`Reply to a message → !truth`")

    def fact_check(self, message: discord.Message) -> str:
        content = message.content
        prompt = PROMPT.format(user_name=message.author.display_name, user_message=content)
        message = CLIENT.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        return message.content[0].text
