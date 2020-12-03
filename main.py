import os
import discord


bot = discord.Client()


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
    if message.author == bot.user:
        return

    kubes = ["koober nets", "kuber nets", "kubernets", "kubernetes"]
    for k in kubes:
        if k in message.content.lower():
            await message.channel.send("I think you mean K8s")
    
    if "bitcoin" in message.content.lower():
        await message.channel.send("Magic Beans*")

    if "tsla" in message.content.lower():
        await message.channel.send("TSLA or SCAM?")
# end def on_message


bot.run(os.environ["TOKEN"])
