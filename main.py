import os
import discord


bot = discord.Client()

def make_correction(author, message):
    kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
    for k in kubes:
        if k in message:
            return "I think {0} means K8s".format(author)
    
    if "bitcoin" in message:
        return "Magic Beans*"

    return None
# end def make_correction


@bot.event
async def on_ready():
    guild_count = 0

    for guild in bot.guilds:
        print(f"- {guild.id} (name: {guild.name})")

        guild_count = guild_count + 1

    print("SampleDiscordBot is in " + str(guild_count) + " guilds.")
# end def on_ready


@bot.event
async def on_message(message):
    author = str(message.author).split("#")[0]
    print(author)

    if message.author == bot.user:
        return

    correction = make_correction(author, message.content.lower())
    if correction is not None:
        await message.channel.send(correction)
# end def on_message


if __name__ == "__main__":
    bot.run(os.environ["TOKEN"])
