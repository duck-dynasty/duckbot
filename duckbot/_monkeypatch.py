import discord.ext.tasks

import duckbot.logs

discord.ext.tasks.loop = duckbot.logs.loop_replacement
