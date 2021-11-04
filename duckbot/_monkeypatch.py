import discord.ext.tasks

import duckbot.logs.loop

discord.ext.tasks.loop = duckbot.logs.loop.loop_replacement
